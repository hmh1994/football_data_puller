from asyncio import run

from football_data_manager.common.repositories.team_stats.team_stat_entity import (
    TeamStatEntity,
)
from football_data_manager.common.repositories.team_stats.team_stat_repository import (
    TeamStatRepository,
)
from football_data_manager.common.services.config.config_service import ConfigService
from football_data_manager.common.services.db.db_service import DbService


# openai_service = OpenAIClientService(api_key=API_KEY, timeout=3600.0)
#
# system_message = """You are a JSON translation engine specialized in translating text values from English to Korean.
# - Preserve the input JSON structure exactly.
# - Translate only the values of "city" and "name" from English to Korean.
# - Do not modify, remove, or reorder any other fields.
#
# Example Input:
# [
#     { "id": "GROUND_42",   "city": "Manchester", "name": "Old Trafford" },
#     { "id": "GROUND_52",   "city": "London",     "name": "Emirates Stadium" },
#     { "id": "GROUND_7305", "city": "Liverpool",  "name": "Anfield" },
#     ...
# ]
#
# Expected output format:
# [
#     { "id": "GROUND_42",   "city": "맨체스터", "name": "올드 트래포드" },
#     { "id": "GROUND_52",   "city": "런던",     "name": "에미레이츠 스타디움" },
#     { "id": "GROUND_7305", "city": "리버풀",   "name": "안필드" },
#     ...
# ]"""
#
#
# def get_user_message(grounds: list[GroundEntity]) -> str:
#     content = dumps(
#         [{"id": g.id, "city": g.city_name_en, "name": g.name_en} for g in grounds]
#     )
#     return f"Translate the following English names into Korean:\n{content}"
#
#
# def chunk_list(lst, chunk_size=10):
#     return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]
#
#
# async def runrun():
#
#     config_service = ConfigService("./configs/.env")
#     db_service = DbService(config_service)
#     ground_repository = GroundRepository(db_service)
#     target_list = chunk_list(await ground_repository.read_all(), 10)
#     print(f"Grounds to translate: {sum(len(t) for t in target_list)}")
#
#     for chunk, targets in enumerate(target_list):
#         user_message = get_user_message(targets)
#         results = await openai_service.request_by_flex_processing(
#             instructions=system_message,
#             message=user_message,
#             model="o4-mini",
#         )
#         print(
#             f"Request #{chunk}:\n{system_message}\n{user_message}\n\nResponse ${chunk}:\n{results}"
#         )
#
#         from regex import compile
#
#         objects = compile(r"\{(?:[^{}]|(?R))*\}").findall(results)
#         translated = [loads(o) for o in objects]
#         print(translated)
#         print(f"Grounds #{chunk} translated: {len(translated)}")
#
#         for idx, target in enumerate(targets):
#             t = next((t for t in translated if t["id"] == target.id), None)
#             if t is None:
#                 print(
#                     f"#{chunk}-{idx}: Ground {target.id} not found in translation results."
#                 )
#                 continue
#             target.city_name_kr = t["city"]
#             target.name_kr = t["name"]
#             await ground_repository.update(target)
#             print(
#                 f"#{chunk}-{idx}: Ground {target.id} updated: {target.city_name_kr}, {target.name_kr}"
#             )
#
#
# run(runrun())


# openai_service = OpenAIClientService(api_key=API_KEY, timeout=3600.0)
#
# system_message = """You are a JSON translation assistant.
# Your task is to take an array of football‐player objects—each with the fields "id", "country", "city" (position), and "name"—and translate the English values of "country", "city", and "name" into Korean Hangul.
# For the "name" field, render each player’s name in Hangul so that it reflects the original pronunciation in the player’s native language as accurately as possible.
# Do not modify the "id" field or the JSON structure, and output only valid JSON.
#
# Example Input:
# ```
# [
#   { "id": "PLAYER_6451", "country": "Slovakia", "city": "Goalkeeper", "name": "Martin Dúbravka" },
#   { "id": "PLAYER_3905", "country": "England", "city": "Right Full Back", "name": "Kieran Trippier" },
#   { "id": "PLAYER_49908", "country": "Netherlands", "city": "Central Defender", "name": "Sven Botman" }
# ]
# ```
#
# Example Output:
# ```
# [
#   { "id": "PLAYER_6451", "country": "슬로바키아", "city": "골키퍼", "name": "마르틴 두브라우카" },
#   { "id": "PLAYER_3905", "country": "영국", "city": "우측 풀백", "name": "키어런 트리피어" },
#   { "id": "PLAYER_49908", "country": "네덜란드", "city": "센터백", "name": "스벤 보트만" }
# ]
# ```
# """
#
#
# def get_user_message(players: list[PlayerEntity]) -> str:
#     content = dumps(
#         [
#             {"id": p.id, "country": p.birth_country_en, "name": p.display_name_en}
#             for p in players
#         ]
#     )
#     return f"Translate the following list:\n```\n{content}\n```"
#
#
# def chunk_list(lst, chunk_size=10):
#     return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]
#
#
# async def run_chunk(
#     chunk: int, targets: list[PlayerEntity], player_repository: PlayerRepository
# ):
#     user_message = get_user_message(targets)
#     results = await openai_service.request_by_flex_processing(
#         instructions=system_message,
#         message=user_message,
#         model="o4-mini",
#     )
#     print(
#         f"Request #{chunk}:\n{system_message}\n{user_message}\n\nResponse ${chunk}:\n{results}"
#     )
#
#     from regex import compile
#
#     objects = compile(r"\{(?:[^{}]|(?R))*\}").findall(results)
#     translated = [loads(o) for o in objects]
#     print(translated)
#     print(f"Players #{chunk} translated: {len(translated)}")
#
#     for idx, target in enumerate(targets):
#         t = next((t for t in translated if t["id"] == target.id), None)
#         if t is None:
#             print(
#                 f"#{chunk}-{idx}: Player {target.id} not found in translation results."
#             )
#             continue
#         target.birth_country_kr = t["country"]
#         target.display_name_kr = t["name"]
#         await player_repository.update(target)
#         print(
#             f"#{chunk}-{idx}: Player {target.id} updated: {target.birth_country_kr}, {target.display_name_kr}"
#         )
#
#
# async def runrun():
#
#     config_service = ConfigService("./configs/.env")
#     db_service = DbService(config_service)
#     player_repository = PlayerRepository(db_service)
#     target_list = chunk_list(await player_repository.read_all(), 10)
#     print(f"Players to translate: {sum(len(t) for t in target_list)}")
#     await gather(
#         *[
#             run_chunk(chunk, targets, player_repository)
#             for chunk, targets in enumerate(target_list)
#         ]
#     )
#
#
# run(runrun())


# openai_service = OpenAIClientService(api_key=API_KEY, timeout=3600.0)
#
# system_message = """You are a JSON translation assistant.
# Your task is to take an array of football‐player objects—each with the fields "id", "country", "city" (position), and "name"—and translate the English values of "country", "city", and "name" into Korean Hangul.
# For the "name" field, render each player’s name in Hangul so that it reflects the original pronunciation in the player’s native language as accurately as possible.
# Do not modify the "id" field or the JSON structure, and output only valid JSON.
#
# Example Input:
# ```
# [
#   { "id": "PLAYER_6451", "country": "Slovakia", "city": "Goalkeeper", "name": "Martin Dúbravka" },
#   { "id": "PLAYER_3905", "country": "England", "city": "Right Full Back", "name": "Kieran Trippier" },
#   { "id": "PLAYER_49908", "country": "Netherlands", "city": "Central Defender", "name": "Sven Botman" }
# ]
# ```
#
# Example Output:
# ```
# [
#   { "id": "PLAYER_6451", "country": "슬로바키아", "city": "골키퍼", "name": "마르틴 두브라우카" },
#   { "id": "PLAYER_3905", "country": "영국", "city": "우측 풀백", "name": "키어런 트리피어" },
#   { "id": "PLAYER_49908", "country": "네덜란드", "city": "센터백", "name": "스벤 보트만" }
# ]
# ```
# """
#
#
# def get_user_message(players: list[PlayerEntity]) -> str:
#     content = dumps(
#         [
#             {"id": p.id, "country": p.birth_country_en, "name": p.display_name_en}
#             for p in players
#         ]
#     )
#     return f"Translate the following list:\n```\n{content}\n```"
#
#
# def chunk_list(lst, chunk_size=10):
#     return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]
#
#
# async def run_chunk(
#     target: PlayerEntity,
#     player_repository: PlayerRepository,
#     positions: dict,
# ):
#     target.position_info_kr = positions.get(target.position_info_en, None)
#     if target.position_info_kr is None:
#         print(f"Position {target.position_info_en} not found in translation results.")
#         return
#     await player_repository.update(target)
#
#
# async def runrun():
#
#     config_service = ConfigService("./configs/.env")
#     db_service = DbService(config_service)
#     player_repository = PlayerRepository(db_service)
#     target_list = await player_repository.read_all()
#     positions = {
#         t["en"]: t["kr"]
#         for t in [
#             {"en": "Central Defender", "kr": "센터백"},
#             {"en": "Centre Defensive Midfielder", "kr": "수비형 미드필더"},
#             {"en": "Left/Centre Second Striker", "kr": "왼쪽/중앙 세컨드 스트라이커"},
#             {"en": "Left Wing Back", "kr": "왼쪽 윙백"},
#             {"en": "Centre Attacking Midfielder", "kr": "중앙 공격형 미드필더"},
#             {"en": "Defender", "kr": "수비수"},
#             {"en": "Attacking Midfielder", "kr": "공격형 미드필더"},
#             {"en": "Striker", "kr": "스트라이커"},
#             {"en": "Centre Central Defender", "kr": "중앙 센터백"},
#             {"en": "Right Full Back", "kr": "오른쪽 풀백"},
#             {
#                 "en": "Left/Centre/Right Second Striker",
#                 "kr": "왼쪽/중앙/오른쪽 세컨드 스트라이커",
#             },
#             {"en": "Left/Centre Central Defender", "kr": "왼쪽/중앙 센터백"},
#             {"en": "Centre Striker", "kr": "중앙 스트라이커"},
#             {"en": "Left/Centre/Right Striker", "kr": "왼쪽/중앙/오른쪽 스트라이커"},
#             {"en": "Forward", "kr": "포워드"},
#             {
#                 "en": "Left/Centre/Right Attacking Midfielder",
#                 "kr": "왼쪽/중앙/오른쪽 공격형 미드필더",
#             },
#             {"en": "Centre/Right Full Back", "kr": "중앙/오른쪽 풀백"},
#             {"en": "Second Striker", "kr": "세컨드 스트라이커"},
#             {"en": "Right Winger", "kr": "오른쪽 윙어"},
#             {
#                 "en": "Left/Centre/Right Central Defender",
#                 "kr": "왼쪽/중앙/오른쪽 센터백",
#             },
#             {"en": "Central Midfielder", "kr": "중앙 미드필더"},
#             {"en": "Left Winger", "kr": "왼쪽 윙어"},
#             {"en": "Left/Centre Winger", "kr": "왼쪽/중앙 윙어"},
#             {"en": "Left Full Back", "kr": "왼쪽 풀백"},
#             {"en": "Centre/Right Central Defender", "kr": "중앙/오른쪽 센터백"},
#             {
#                 "en": "Centre/Right Attacking Midfielder",
#                 "kr": "중앙/오른쪽 공격형 미드필더",
#             },
#             {"en": "Full Back", "kr": "풀백"},
#             {"en": "Centre Second Striker", "kr": "중앙 세컨드 스트라이커"},
#             {"en": "Centre Central Midfielder", "kr": "중앙 중앙 미드필더"},
#             {"en": "Left/Centre/Right Winger", "kr": "왼쪽/중앙/오른쪽 윙어"},
#             {"en": "Goalkeeper", "kr": "골키퍼"},
#             {"en": "Left/Centre Striker", "kr": "왼쪽/중앙 스트라이커"},
#             {"en": "Midfielder", "kr": "미드필더"},
#             {"en": "Left/Right Winger", "kr": "왼쪽/오른쪽 윙어"},
#             {
#                 "en": "Left/Centre/Right Central Midfielder",
#                 "kr": "왼쪽/중앙/오른쪽 중앙 미드필더",
#             },
#             {
#                 "en": "Left/Centre Attacking Midfielder",
#                 "kr": "왼쪽/중앙 공격형 미드필더",
#             },
#             {"en": "Defensive Midfielder", "kr": "수비형 미드필더"},
#             {"en": "Winger", "kr": "윙어"},
#         ]
#     }
#     await gather(
#         *[run_chunk(target, player_repository, positions) for target in target_list]
#     )


# async def convert(db_service, target):
#     team_repo = TeamRepository(db_service)
#     teams = await gather(
#         *[
#             team_repo.read_by_source_id(source=SourceEnum.PULSELIVE, source_id=t)
#             for t in target.teams
#         ]
#     )
#     return NewsEntity(
#         author_en=target.author_en,
#         author_kr=target.author_kr,
#         content_en=target.content_en,
#         content_kr=target.content_kr,
#         publish_date=target.publish_date,
#         url=target.url,
#         source=SourceEnum.THE_ATHLETIC,
#         source_id=target.id.removeprefix("THEATHLETIC_NEWS_"),
#         teams=[t.id for t in teams if t is not None],
#         thumbnail_url=target.thumbnail_url,
#         title_en=target.title_en,
#         title_kr=target.title_kr,
#         typ=NewsTypeEnum.from_string(target.type),
#     )
#
#
# async def runrun():
#
#     config_service = ConfigService("./configs/.env")
#     db_service = DbService(config_service)
#     async with db_service.engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#     old_repo = OldNewsRepository(db_service)
#     target_list = await old_repo.read_all()
#     new_targets = await gather(*[convert(db_service, t) for t in target_list])
#     new_repo = NewsRepository(db_service)
#     await new_repo.create_all(new_targets, NewsEntity.get_id)


async def runrun():

    config_service = ConfigService("./configs/.env")
    db_service = DbService(config_service)
    repo = TeamStatRepository(db_service)
    targets = await repo.read_all()
    targets_per_season: dict[str, list[TeamStatEntity]] = {}
    for target in targets:
        if target.season_id not in targets_per_season:
            targets_per_season[target.season_id] = []
        targets_per_season[target.season_id].append(target)
    for _, ts in targets_per_season.items():
        for t in ts:
            t.overall_matches_won = t.home_matches_won + t.away_matches_won
            t.overall_points = t.home_points + t.away_points
        for t in ts:
            t.overall_position = 1 + len(
                [i for i in ts if i.overall_points > t.overall_points]
            )
            await repo.update(t)


run(runrun())
