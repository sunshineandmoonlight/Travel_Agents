"""
测试目的地数据库扩展结果
"""
import sys
sys.path.insert(0, '.')

from tradingagents.agents.group_a.destination_matcher import DOMESTIC_DESTINATIONS_DB, INTERNATIONAL_DESTINATIONS_DB

print('=' * 60)
print('目的地数据库扩展结果')
print('=' * 60)

print('\n【国内城市】')
print(f'总数: {len(DOMESTIC_DESTINATIONS_DB)} 个')
domestic_cities = sorted(DOMESTIC_DESTINATIONS_DB.keys())
for i, city in enumerate(domestic_cities, 1):
    tags = DOMESTIC_DESTINATIONS_DB[city].get('tags', [])
    print(f'{i:2}. {city}')

print('\n【国际目的地】')
print(f'总数: {len(INTERNATIONAL_DESTINATIONS_DB)} 个')
international_countries = sorted(INTERNATIONAL_DESTINATIONS_DB.keys())
for i, country in enumerate(international_countries, 1):
    name_en = INTERNATIONAL_DESTINATIONS_DB[country].get('name_en', '')
    tags = INTERNATIONAL_DESTINATIONS_DB[country].get('tags', [])
    print(f'{i:2}. {country} ({name_en})')

print('\n' + '=' * 60)
print(f'扩展完成！')
print(f'  国内: {len(DOMESTIC_DESTINATIONS_DB)} 个城市')
print(f'  国际: {len(INTERNATIONAL_DESTINATIONS_DB)} 个国家')
print(f'  总计: {len(DOMESTIC_DESTINATIONS_DB) + len(INTERNATIONAL_DESTINATIONS_DB)} 个目的地')
print('=' * 60)
