from aiohttp import web
import json
from database import get_user, update_balance, update_inventory, update_bonus_claim
import random
import time

# Настройки кейсов
CASE_SETTINGS = {
    "gift_box": {
        "price": 25,
        "items": [
            {"gift": "🧸", "price": 15, "chance": 35},
            {"gift": "💝", "price": 15, "chance": 35},
            {"gift": "🌹", "price": 25, "chance": 7.5},
            {"gift": "🎁", "price": 25, "chance": 7.5},
            {"gift": "🚀", "price": 50, "chance": 5},
            {"gift": "🍾", "price": 50, "chance": 5},
            {"gift": "🏆", "price": 100, "chance": 2.5},
            {"gift": "💍", "price": 100, "chance": 2.5}
        ]
    }
}

# Настройки рулетки
ROULETTE_SETTINGS = {
    "price": 50,
    "items": [
        {"gift": "🧸", "price": 15, "chance": 34.5},
        {"gift": "💝", "price": 15, "chance": 34.5},
        {"gift": "🌹", "price": 25, "chance": 7.5},
        {"gift": "🎁", "price": 25, "chance": 7.5},
        {"gift": "🚀", "price": 50, "chance": 5},
        {"gift": "🍾", "price": 50, "chance": 5},
        {"gift": "🏆", "price": 100, "chance": 2.5},
        {"gift": "💍", "price": 100, "chance": 2.5},
        {"gift": "❔", "price": 0, "chance": 1, "name": "Random NFT Gift"}
    ]
}

async def get_user_data(request):
    """Получить данные пользователя"""
    user_id = int(request.query.get('user_id'))
    user_data = await get_user(user_id)
    
    if user_data:
        return web.json_response({
            'success': True,
            'user': user_data
        })
    else:
        return web.json_response({
            'success': False,
            'error': 'User not found'
        })

async def open_case(request):
    """Открыть кейс"""
    data = await request.json()
    user_id = data.get('user_id')
    case_type = data.get('case_type')
    
    user_data = await get_user(user_id)
    if not user_data:
        return web.json_response({'success': False, 'error': 'User not found'})
    
    case = CASE_SETTINGS.get(case_type)
    if not case:
        return web.json_response({'success': False, 'error': 'Invalid case type'})
    
    # Проверка баланса
    if user_data['balance'] < case['price']:
        return web.json_response({'success': False, 'error': 'Not enough stars'})
    
    # Случайный выбор подарка
    rand = random.random() * 100
    current_chance = 0
    
    for item in case['items']:
        current_chance += item['chance']
        if rand <= current_chance:
            won_item = item.copy()
            break
    
    # Обновление баланса и инвентаря
    await update_balance(user_id, -case['price'])
    
    new_inventory = user_data['inventory'] + [won_item]
    await update_inventory(user_id, new_inventory)
    
    # Обновление данных пользователя
    user_data['balance'] -= case['price']
    user_data['inventory'] = new_inventory
    
    return web.json_response({
        'success': True,
        'won_item': won_item,
        'new_balance': user_data['balance'],
        'inventory': new_inventory
    })

async def spin_roulette(request):
    """Крутить рулетку"""
    data = await request.json()
    user_id = data.get('user_id')
    
    user_data = await get_user(user_id)
    if not user_data:
        return web.json_response({'success': False, 'error': 'User not found'})
    
    # Проверка баланса
    if user_data['balance'] < ROULETTE_SETTINGS['price']:
        return web.json_response({'success': False, 'error': 'Not enough stars'})
    
    # Случайный выбор подарка
    rand = random.random() * 100
    current_chance = 0
    
    for item in ROULETTE_SETTINGS['items']:
        current_chance += item['chance']
        if rand <= current_chance:
            won_item = item.copy()
            break
    
    # Обновление баланса и инвентаря
    await update_balance(user_id, -ROULETTE_SETTINGS['price'])
    
    new_inventory = user_data['inventory'] + [won_item]
    await update_inventory(user_id, new_inventory)
    
    # Обновление данных пользователя
    user_data['balance'] -= ROULETTE_SETTINGS['price']
    user_data['inventory'] = new_inventory
    
    return web.json_response({
        'success': True,
        'won_item': won_item,
        'new_balance': user_data['balance'],
        'inventory': new_inventory
    })

async def claim_bonus(request):
    """Получить бонусный кейс"""
    data = await request.json()
    user_id = data.get('user_id')
    
    user_data = await get_user(user_id)
    if not user_data:
        return web.json_response({'success': False, 'error': 'User not found'})
    
    current_time = int(time.time())
    last_claim = user_data['last_bonus_claim']
    
    # Проверка времени (24 часа)
    if current_time - last_claim < 86400:
        return web.json_response({'success': False, 'error': 'Bonus not available yet'})
    
    # Начисление бонуса (1-5 звезд)
    bonus_stars = random.randint(1, 5)
    await update_balance(user_id, bonus_stars)
    await update_bonus_claim(user_id, current_time)
    
    user_data['balance'] += bonus_stars
    user_data['last_bonus_claim'] = current_time
    
    return web.json_response({
        'success': True,
        'bonus_stars': bonus_stars,
        'new_balance': user_data['balance'],
        'next_bonus': current_time + 86400
    })

async def sell_item(request):
    """Продать предмет из инвентаря"""
    data = await request.json()
    user_id = data.get('user_id')
    item_index = data.get('item_index')
    
    user_data = await get_user(user_id)
    if not user_data:
        return web.json_response({'success': False, 'error': 'User not found'})
    
    if item_index >= len(user_data['inventory']):
        return web.json_response({'success': False, 'error': 'Invalid item index'})
    
    # Получаем предмет
    item = user_data['inventory'][item_index]
    sell_price = int(item['price'] * 1.2)  # Продажа за 120% цены
    
    # Удаляем предмет из инвентаря и добавляем звезды
    new_inventory = user_data['inventory'].copy()
    new_inventory.pop(item_index)
    
    await update_balance(user_id, sell_price)
    await update_inventory(user_id, new_inventory)
    
    user_data['balance'] += sell_price
    user_data['inventory'] = new_inventory
    
    return web.json_response({
        'success': True,
        'sold_item': item,
        'sell_price': sell_price,
        'new_balance': user_data['balance'],
        'inventory': new_inventory
    })

def setup_routes(app):
    """Настройка маршрутов"""
    app.router.add_get('/api/user', get_user_data)
    app.router.add_post('/api/open_case', open_case)
    app.router.add_post('/api/spin_roulette', spin_roulette)
    app.router.add_post('/api/claim_bonus', claim_bonus)
    app.router.add_post('/api/sell_item', sell_item)