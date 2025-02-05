from .. import bp
from flask import render_template, current_app, request, redirect, url_for
from jeec_brain.finders.meals_finder import MealsFinder
from jeec_brain.finders.companies_finder import CompaniesFinder
from jeec_brain.handlers.meals_handler import MealsHandler
from jeec_brain.services.meals.get_meal_types_service import GetMealTypesService
from jeec_brain.services.meals.get_dish_types_service import GetDishTypesService
from jeec_brain.values.api_error_value import APIErrorValue
from jeec_brain.apps.auth.wrappers import allowed_roles, allow_all_roles
from jeec_brain.models.enums.meal_type_enum import MealTypeEnum
from jeec_brain.models.enums.dish_type_enum import DishTypeEnum
from jeec_brain.schemas.admin_api.meals.schemas import *
from datetime import datetime
from flask_login import current_user


# Meals routes
@bp.get("/meals")
@allow_all_roles
def meals_dashboard():
    search_parameters = request.args
    day = request.args.get("day")

    # handle search bar requests
    if day is not None:
        search = day
        meals_list = MealsFinder.get_meals_from_day(day)

    # handle parameter requests
    elif len(search_parameters) != 0:
        search_parameters = request.args
        search = "search by day"

        meals_list = MealsFinder.get_meals_from_parameters(search_parameters)

    # request endpoint with no parameters should return all meals
    else:
        search = None
        meals_list = MealsFinder.get_all_meals()

    if meals_list is None or len(meals_list) == 0:
        error = "No results found"
        return render_template(
            "admin/meals/meals_dashboard.html",
            meals=None,
            error=error,
            search=search,
            role=current_user.role.name,
        )

    return render_template(
        "admin/meals/meals_dashboard.html",
        meals=meals_list,
        error=None,
        search=search,
        role=current_user.role.name,
    )


@bp.get("/new-meal")
@allowed_roles(["admin", "companies_admin"])
def add_meal_dashboard():
    companies = CompaniesFinder.get_all()
    meal_types = GetMealTypesService.call()
    dish_types = GetDishTypesService.call()
    return render_template(
        "admin/meals/add_meal.html",
        meal_types=meal_types,
        dish_types=dish_types,
        companies=companies,
        error=None,
    )


@bp.post("/new-meal")
@allowed_roles(["admin", "companies_admin"])
def create_meal():
    # extract form parameters
    meal_type = request.form.get("type")
    location = request.form.get("location")
    day = request.form.get("day")
    time = request.form.get("time")
    registration_day = request.form.get("registration_day")
    registration_time = request.form.get("registration_time")

    if meal_type not in GetMealTypesService.call():
        return "Wrong meal type provided", 404
    else:
        meal_type = MealTypeEnum[meal_type]

    # create new meal
    meal = MealsHandler.create_meal(
        type=meal_type,
        location=location,
        day=day,
        time=time,
        registration_day=registration_day,
        registration_time=registration_time,
    )

    if meal is None:
        return render_template(
            "admin/meals/add_meal.html",
            type=meal_type,
            companies=CompaniesFinder.get_all(),
            error="Failed to create meal!",
        )

    # extract company names and max dish quantities from parameters
    companies = request.form.getlist("company")
    max_dish_quantities = request.form.getlist("max_dish_quantity")

    # if company names where provided
    if companies:
        for index, name in enumerate(companies):
            company = CompaniesFinder.get_from_name(name)
            if company is None:
                return APIErrorValue("Couldnt find company").json(500)

            try:
                max_dish_quantity = int(max_dish_quantities[index])
            except:
                max_dish_quantity = None

            company_meal = MealsHandler.add_company_meal(
                company, meal, max_dish_quantity
            )
            if company_meal is None:
                return APIErrorValue("Failed to create company meal").json(500)

    # extract dish names and descriptions from parameters
    dish_names = request.form.getlist("dish_name")
    dish_descriptions = request.form.getlist("dish_description")
    dish_types = request.form.getlist("dish_type")

    # if dishes names where provided
    if dish_names:
        for index, name in enumerate(dish_names):
            if not name:
                continue

            try:
                dish_description = dish_descriptions[index]
            except:
                dish_description = None

            try:
                dish_type = dish_types[index]
            except:
                dish_type = None

            if dish_type not in GetDishTypesService.call():
                return "Wrong dish type provided", 404
            else:
                dish_type = DishTypeEnum[dish_type]

            meal_dish = MealsHandler.create_dish(
                name=name, description=dish_description, meal_id=meal.id, type=dish_type
            )
            if meal_dish is None:
                return APIErrorValue("Failed to create dish").json(500)

    return redirect(url_for("admin_api.meals_dashboard"))


@bp.get("/meal/<string:meal_external_id>")
@allowed_roles(["admin", "companies_admin"])
def get_meal(path: MealPath):
    meal = MealsFinder.get_meal_from_external_id(path.meal_external_id)
    companies = CompaniesFinder.get_all()
    meal_types = GetMealTypesService.call()
    dish_types = GetDishTypesService.call()
    company_meals = MealsFinder.get_company_meals_from_meal_id(path.meal_external_id)
    dishes = MealsFinder.get_dishes_from_meal_id(path.meal_external_id)

    return render_template(
        "admin/meals/update_meal.html",
        meal=meal,
        meal_types=meal_types,
        dish_types=dish_types,
        companies=companies,
        company_meals=[company.company_id for company in company_meals],
        dishes=dishes,
        error=None,
    )


@bp.post("/meal/<string:meal_external_id>")
@allowed_roles(["admin", "companies_admin"])
def update_meal(path: MealPath):
    meal = MealsFinder.get_meal_from_external_id(path.meal_external_id)
    company_meals = MealsFinder.get_company_meals_from_meal_id(path.meal_external_id)
    dishes = MealsFinder.get_dishes_from_meal_id(path.meal_external_id)

    if meal is None:
        return APIErrorValue("Couldnt find meal").json(500)

    # extract form parameters
    meal_type = request.form.get("type")
    location = request.form.get("location")
    day = request.form.get("day")
    time = request.form.get("time")
    registration_day = request.form.get("registration_day")
    registration_time = request.form.get("registration_time")

    if meal_type not in GetMealTypesService.call():
        return "Wrong meal type provided", 404
    else:
        meal_type = MealTypeEnum[meal_type]

    updated_meal = MealsHandler.update_meal(
        meal=meal,
        type=meal_type,
        location=location,
        day=day,
        time=time,
        registration_day=registration_day,
        registration_time=registration_time,
    )

    previous_companies = [company_meal.company_id for company_meal in company_meals]

    if company_meals:
        for company_meal in company_meals:
            MealsHandler.delete_company_meal(company_meal)

    # extract company names and max dish quantities from parameters
    companies = request.form.getlist("company")
    max_dish_quantities = request.form.getlist("max_dish_quantity")

    updated_companies = []

    # if company names where provided
    if companies:
        for index, name in enumerate(companies):
            company = CompaniesFinder.get_from_name(name)
            if company is None:
                return APIErrorValue("Couldnt find company").json(500)

            updated_companies.append(company.id)

            try:
                max_dish_quantity = max_dish_quantities[index]
            except:
                max_dish_quantity = None

            company_meal = MealsHandler.add_company_meal(
                company, meal, max_dish_quantity
            )
            if company_meal is None:
                return APIErrorValue("Failed to create company meal").json(500)

    # delete dishes from deleted companies
    for company_id in previous_companies:
        if company_id not in updated_companies:
            company_dishes = MealsFinder.get_company_dishes_from_meal_id_and_company_id(
                meal.id, company_id
            )

            if company_dishes:
                for company_dish in company_dishes:
                    MealsHandler.delete_company_dish(company_dish)

    # extract dish names and descriptions from parameters
    dish_names = request.form.getlist("dish_name")
    dish_descriptions = request.form.getlist("dish_description")
    dish_types = request.form.getlist("dish_type")

    previous_dish_names = [dish.name for dish in dishes]
    previous_dish_descriptions = [dish.description for dish in dishes]
    previous_dish_types = [dish.type for dish in dishes]

    updated_dishes = []

    # if dishes names where provided
    if dish_names:
        for index, name in enumerate(dish_names):
            if not name:
                continue

            try:
                dish_description = dish_descriptions[index]
            except:
                pass

            try:
                dish_type = dish_types[index]
            except:
                dish_type = None

            if dish_type not in GetDishTypesService.call():
                return "Wrong dish type provided", 404
            else:
                dish_type = DishTypeEnum[dish_type]

            # if dish name already exists
            if name in previous_dish_names:
                # if dish already exists do nothing
                if (
                    dish_description
                    == previous_dish_descriptions[previous_dish_names.index(name)]
                    and dish_type
                    == previous_dish_types[previous_dish_names.index(name)]
                ):
                    updated_dishes.append(dishes[previous_dish_names.index(name)])
                    continue

                # if descrition or type is changed, update it
                updated_dish = MealsHandler.update_dish(
                    dish=dishes[previous_dish_names.index(name)],
                    name=name,
                    description=dish_description,
                    meal_id=meal.id,
                    type=dish_type,
                )
                if updated_dish is None:
                    return APIErrorValue("Failed to update dish").json(500)

                updated_dishes.append(updated_dish)
                continue

            # if dish doesnt exist, create it
            created_dish = MealsHandler.create_dish(
                name=name, description=dish_description, meal_id=meal.id, type=dish_type
            )

            if created_dish is None:
                return APIErrorValue("Failed to create dish").json(500)

    # delete non updated dishes
    if dishes:
        for dish in dishes:
            if dish in updated_dishes:
                continue

            company_dishes = MealsFinder.get_company_dishes_from_dish_id(dish.id)

            if company_dishes:
                for company_dish in company_dishes:
                    MealsHandler.delete_company_dish(company_dish)

            MealsHandler.delete_dish(dish)

    if updated_meal is None:
        return render_template(
            "admin/meals/update_meal.html",
            meal=meal,
            types=GetMealTypesService.call(),
            companies=CompaniesFinder.get_all(),
            error="Failed to update meal!",
        )

    return redirect(url_for("admin_api.meals_dashboard"))


@bp.get("/meal/<string:meal_external_id>/delete")
@allowed_roles(["admin", "companies_admin"])
def delete_meal(path: MealPath):
    meal = MealsFinder.get_meal_from_external_id(path.meal_external_id)
    company_meals = MealsFinder.get_company_meals_from_meal_id(path.meal_external_id)
    dishes = MealsFinder.get_dishes_from_meal_id(path.meal_external_id)

    if meal is None:
        return APIErrorValue("Couldnt find meal").json(500)

    if company_meals:
        for company_meal in company_meals:
            MealsHandler.delete_company_meal(company_meal)

    if dishes:
        for dish in dishes:
            company_dishes = MealsFinder.get_company_dishes_from_dish_id(dish.id)

            if company_dishes:
                for company_dish in company_dishes:
                    MealsHandler.delete_company_dish(company_dish)

            MealsHandler.delete_dish(dish)

    if MealsHandler.delete_meal(meal):
        return redirect(url_for("admin_api.meals_dashboard"))

    else:
        return render_template(
            "admin/meals/update_meal.html", meal=meal, error="Failed to delete meal!"
        )


@bp.get("/meal/<string:meal_external_id>/dishes")
@allowed_roles(["admin", "companies_admin"])
def meal_dishes(path: MealPath):
    meal = MealsFinder.get_meal_from_external_id(path.meal_external_id)

    if meal is None:
        return APIErrorValue("Couldnt find meal").json(500)

    company_dishes = MealsFinder.get_dishes_per_company_from_meal_id(meal.id)
    dishes = MealsFinder.get_dishes_from_meal_id(path.meal_external_id)
    dishes_per_companies = {}

    for company_dish in company_dishes:
        try:
            dishes_per_companies[company_dish[0]].append(
                [company_dish[1], company_dish[2]]
            )
        except KeyError:
            dishes_per_companies.update({company_dish[0]: []})
            dishes_per_companies[company_dish[0]].append(
                [company_dish[1], company_dish[2]]
            )

    total_dishes = []

    for dish in dishes:
        choosen_dishes = MealsFinder.get_company_dishes_from_dish_id(dish.id)
        total_dishes.append(
            sum([choosen_dish.dish_quantity for choosen_dish in choosen_dishes])
        )

    try:
        registration_time = datetime.strptime(
            meal.registration_day + " " + meal.registration_time, "%d %m %Y, %a %H:%M"
        )
        closed = False

        # check if date past registration date
        if registration_time < datetime.now():
            closed = True
    except:
        closed = True

    return render_template(
        "admin/meals/meal_dishes.html",
        meal=meal,
        dishes=dishes,
        dishes_per_companies=dishes_per_companies,
        total_dishes=total_dishes,
        closed=closed,
    )
