group_token = ''
access_token = ''
# количество пользователей для выдачи
count = 50


explorer_scopes  = [
    "bdate",
    "sex",
    "city",
    "relation"
]

explorer_fields   = ",".join(explorer_scopes)

explorer_data  = {
    "bdate": 0,
    "sex": 0,
    "city_id": 0,
    "city": 0,
    "relation": 0
}

partner_data  = {
    "first_name": 0,
    "last_name": 0,
    "id": 0
}

all_partner_data  = list()

male_sex_terms  = [
    "2", "мужской", "парень", "мужик", "муж", "м", "мужчинка", "мачо",
    "молодой человек", "дядька", "мужчина", "мэн", "дядя", "мистер",
    "сильный пол", "man", "m", "male"
]

female_sex_terms  = [
    "1", "женский", "женщина", "девушка", "девочка", "леди", "богиня",
    "королева", "принцесса", "дама", "царица", "гражданка", "дева", "мадам",
    "дамочка", "мисс", "миссис", "сударыня", "прекрасный пол", "нежный пол",
    "слабый пол", "миледи", "woman", "girl", "female", "lady", "w", "f"
]

potential_relationships  = [str(x) for x in range(9)]

