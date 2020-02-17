from jeec_brain.apps.companies_api import bp
from flask import render_template, session, request, redirect, url_for
from flask_login import current_user
from jeec_brain.apps.auth.wrappers import require_company_login
from jeec_brain.finders.companies_finder import CompaniesFinder
from jeec_brain.handlers.companies_handler import CompaniesHandler
from jeec_brain.finders.meals_finder import MealsFinder
from jeec_brain.handlers.meals_handler import MealsHandler
from jeec_brain.values.api_error_value import APIErrorValue
from datetime import datetime


@bp.route('/meals', methods=['GET'])
@require_company_login
def meals_dashboard():
    if current_user.company is None:
        return APIErrorValue('Couldnt find company').json(400)

    meals_list = current_user.company.meals

    if meals_list is None or len(meals_list) == 0:
        error = 'No meals found'
        return render_template('admin/meals/meals_dashboard.html', meals=None, error=error, company=current_user.company)

    return render_template('companies/meals/meals_dashboard.html', meals=meals_list, error=None, company=current_user.company)


@bp.route('/meal/<string:meal_external_id>', methods=['GET'])
@require_company_login
def get_meal(meal_external_id):
    if current_user.company is None:
        return APIErrorValue('Couldnt find company').json(400)

    # get meal
    meal = MealsFinder.get_meal_from_external_id(meal_external_id)

    if meal is None:
        return APIErrorValue('Couldnt find meal').json(400)

    # check if company is allowed in meal
    if current_user.company not in MealsFinder.get_companies_from_meal_id(meal.id):
        return APIErrorValue('Company not allowed in this meal').json(400)

    # get company meal
    company_meal = MealsFinder.get_company_meals_from_meal_id_and_company_id(meal.id, current_user.company_id)

    if company_meal is None:
        return APIErrorValue('Couldnt find company meal').json(400)

    # get dishes from meal
    dishes = MealsFinder.get_dishes_from_meal_id(meal_external_id)

    if dishes is None:
        return render_template('companies/meals/meal.html', \
            meal=meal, \
            max_dish_quantity=None, \
            dishes=None, \
            error='No dishes found.', \
            user=current_user)

    return render_template('companies/meals/meal.html', \
        meal=meal, \
        max_dish_quantity=company_meal.max_dish_quantity, \
        dishes=dishes,
        error=None, \
        user=current_user)


@bp.route('/meal/<string:meal_external_id>', methods=['POST'])
@require_company_login
def choose_dishes(meal_external_id):
    if current_user.company is None:
        return APIErrorValue('Couldnt find company').json(400)
    
    # get meal
    meal = MealsFinder.get_meal_from_external_id(meal_external_id)
    registration_time = datetime.strptime(meal.registration_day + ' ' + meal.registration_time, '%b %d, %Y %I:%M %p')

    # check if date past registration date
    if registration_time > datetime.now():
        return APIErrorValue('Past registration time. Cant choose meal.').json(400)

    # eliminate previous company dishes
    company_dishes = MealsFinder.get_company_dishes_from_meal_id_and_company_id(meal.id, current_user.company_id)

    if company_dishes:
        for company_dish in company_dishes:
            MealsHandler.delete_company_dish(company_dish)

    # get company meal
    company_meal = MealsFinder.get_company_meals_from_meal_id_and_company_id(meal.id, current_user.company_id)

    if company_meal is None:
        return APIErrorValue('Couldnt find company meal').json(400)

    # get dishes
    dish_ids = request.form.getlist('dish')
    dish_quantities = request.form.getlist('dish_quantity')
    
    try:
        if sum(list(map(int, filter(None, dish_quantities)))) > company_meal.max_dish_quantity:
            return APIErrorValue('Number of dishes over maximum value!').json(500)
    except Exception as e:
        return APIErrorValue('Quantities type not int' + str(e))
        
    if dish_ids:
        for index, dish_id in enumerate(dish_ids):
            dish = MealsFinder.get_dishes_from_dish_external_id(dish_id)

            if dish is None:
                return APIErrorValue('Couldnt find dish').json(500)

            try:
                dish_quantity = int(dish_quantities[index])
            except ValueError:
                continue
            except TypeError:
                continue
            except IndexError:
                return APIErrorValue('Quantities size different from dishes').json(500)

            MealsHandler.add_company_dish(
                company=current_user.company,
                dish=dish,
                dish_quantity=dish_quantity
            )

    return redirect(url_for('companies_api.meals_dashboard'))

