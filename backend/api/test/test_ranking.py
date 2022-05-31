from port.port import RankingStore


def set_score(phone_id: str, ranking_store: RankingStore, count: int):
    for _ in range(count):
        ranking_store.add_full_score(phone_id)


def test_global_return_count_asked(ranking_service, ranking_store):
    set_score("id2", ranking_store, 2)
    set_score("id4", ranking_store, 4)
    set_score("id1", ranking_store, 1)
    set_score("id3", ranking_store, 3)
    set_score("id4", ranking_store, 5)
    ranking = ranking_service.global_ranking(3)
    assert len(ranking) == 3


def test_global_return_more_if_exaequo(ranking_service, ranking_store):
    set_score("id1", ranking_store, 5)
    set_score("id2", ranking_store, 5)
    set_score("id3", ranking_store, 4)
    set_score("id4", ranking_store, 4)
    set_score("id5", ranking_store, 4)
    set_score("id6", ranking_store, 4)
    set_score("id7", ranking_store, 2)
    set_score("id8", ranking_store, 2)
    ranking = ranking_service.global_ranking(3)
    assert len(ranking) == 6