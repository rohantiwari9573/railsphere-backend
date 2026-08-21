async def _gql(client, query: str, variables: dict | None = None):
    response = await client.post(
        "/graphql", json={"query": query, "variables": variables or {}}
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert "errors" not in body, body
    return body["data"]


async def test_station_query_returns_created_station(client):
    created = await client.post(
        "/stations", json={"code": "GQL1", "name": "GraphQL Junction"}
    )
    station_id = created.json()["id"]

    data = await _gql(
        client,
        "query($id: Int!) { station(id: $id) { id code name isActive } }",
        {"id": station_id},
    )

    assert data["station"] == {
        "id": station_id,
        "code": "GQL1",
        "name": "GraphQL Junction",
        "isActive": True,
    }


async def test_station_query_returns_null_for_missing_id(client):
    data = await _gql(
        client, "query { station(id: 999999) { id } }"
    )
    assert data["station"] is None


async def test_stations_query_search_filters_results(client):
    await client.post(
        "/stations", json={"code": "GQL2", "name": "Search Target Halt"}
    )
    await client.post(
        "/stations", json={"code": "GQL3", "name": "Unrelated Stop"}
    )

    data = await _gql(
        client,
        'query { stations(search: "Search Target", limit: 5) { code name } }',
    )

    codes = [s["code"] for s in data["stations"]]
    assert "GQL2" in codes
    assert "GQL3" not in codes


async def test_train_query_returns_created_train(client):
    created = await client.post(
        "/trains",
        json={
            "train_number": "GQ100",
            "train_name": "GraphQL Express",
            "train_type": "Express",
        },
    )
    train_id = created.json()["id"]

    data = await _gql(
        client,
        "query($id: Int!) { train(id: $id) { id trainNumber trainName } }",
        {"id": train_id},
    )

    assert data["train"]["trainNumber"] == "GQ100"
    assert data["train"]["trainName"] == "GraphQL Express"


async def test_route_query_returns_created_route(client):
    created = await client.post(
        "/routes",
        json={"route_code": "GQR1", "route_name": "GraphQL Route"},
    )
    route_id = created.json()["id"]

    data = await _gql(
        client,
        "query($id: Int!) { route(id: $id) { id routeCode routeName } }",
        {"id": route_id},
    )

    assert data["route"]["routeCode"] == "GQR1"
    assert data["route"]["routeName"] == "GraphQL Route"
