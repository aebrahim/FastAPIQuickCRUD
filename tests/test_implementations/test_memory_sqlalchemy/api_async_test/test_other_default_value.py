import json
import os
from copy import deepcopy
from datetime import datetime, timezone, date, timedelta
from http import HTTPStatus
from urllib.parse import urlencode

from fastapi import FastAPI
from sqlalchemy import BigInteger, Boolean, CHAR, Column, Date, DateTime, Float, Integer, \
    LargeBinary, Numeric, SmallInteger, String, Text, Time, UniqueConstraint, func
from sqlalchemy.orm import declarative_base
from starlette.testclient import TestClient

from src.fastapi_quickcrud.crud_router import crud_router_builder
from src.fastapi_quickcrud.misc.type import CrudMethods

TEST_DATABASE_URL = os.environ.get('TEST_DATABASE_URL', 'postgresql://postgres:1234@127.0.0.1:5432/postgres')

app = FastAPI()

Base = declarative_base()
metadata = Base.metadata


class UUIDTable(Base):
    primary_key_of_table = "primary_key"
    unique_fields = ['primary_key', 'int4_value', 'float4_value']
    __tablename__ = 'test_default_value_sync'
    __table_args__ = (
        UniqueConstraint('primary_key', 'int4_value', 'float4_value'),
    )
    primary_key = Column(Integer, primary_key=True, autoincrement=True)
    bool_value = Column(Boolean, nullable=False, default=False)
    bytea_value = Column(LargeBinary)
    char_value = Column(CHAR(10))
    date_value = Column(Date, default=datetime.now())
    float4_value = Column(Float, nullable=False)
    float8_value = Column(Float(53), nullable=False, default=10)
    int2_value = Column(SmallInteger, nullable=False)
    int4_value = Column(Integer, nullable=False)
    int8_value = Column(BigInteger, default=99)
    numeric_value = Column(Numeric)
    text_value = Column(Text)
    time_value = Column(Time)
    timestamp_value = Column(DateTime)
    timestamptz_value = Column(DateTime(True))
    timetz_value = Column(Time(True))
    varchar_value = Column(String)


route_1 = crud_router_builder(db_model=UUIDTable,
                              crud_methods=[
                                  CrudMethods.FIND_ONE,
                                  CrudMethods.FIND_MANY,
                                  CrudMethods.CREATE_MANY,
                                  CrudMethods.UPDATE_ONE,
                                  CrudMethods.UPDATE_MANY,
                                  CrudMethods.PATCH_MANY,
                                  CrudMethods.PATCH_ONE,
                                  CrudMethods.DELETE_MANY,
                                  CrudMethods.DELETE_ONE,
                              ],
                              exclude_columns=['bytea_value', 'xml_value', 'box_valaue'],
                              prefix="/test",
                              tags=["test"],
                              async_mode=True
                              )

route_2 = crud_router_builder(db_model=UUIDTable,
                              crud_methods=[
                                  CrudMethods.CREATE_ONE,
                                  CrudMethods.POST_REDIRECT_GET,
                              ],
                              exclude_columns=['bytea_value', 'xml_value', 'box_valaue'],
                              prefix="/test_2",
                              tags=["test"],
                              async_mode=True
                              )

route_3 = crud_router_builder(db_model=UUIDTable,
                              crud_methods=[
                                  CrudMethods.FIND_ONE,
                                  CrudMethods.POST_REDIRECT_GET,
                              ],
                              exclude_columns=['bytea_value', 'xml_value', 'box_valaue'],
                              prefix="/test_3",
                              tags=["test"],
                              async_mode=True
                              )

[app.include_router(i) for i in [route_1, route_2, route_3]]

client = TestClient(app)


def test_get_one_data_and_create_one_data():
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }
    data = '{"float4_value": 0, "int2_value": 0, "int4_value": 0 }'
    response = client.post('/test_2', headers=headers, data=data)
    assert response.status_code == 201
    create_response = response.json()
    find_target = create_response['primary_key']
    response = client.get(f'/test/{find_target}', headers=headers, data=data)
    assert response.status_code == 200
    assert response.json() == create_response
    create_response.pop('primary_key')
    query_param = urlencode(create_response)
    response = client.get(f'/test/{find_target}?{query_param}', headers=headers, data=data)
    assert response.status_code == 200


def test_get_many_data_and_create_many_data():
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }

    data = ''' [ { "char_value": "string    ", "date_value": "2021-07-23", "float4_value": 0, "float8_value": 0, "int2_value": 0, "int4_value": 0, "int8_value": 0, "numeric_value": 0, "text_value": "string", "timestamp_value": "2021-07-23T02:38:24.963000", "timestamptz_value": "2021-07-23T02:38:24.963000+00:00","varchar_value": "string"}, {  "char_value": "string    ", "date_value": "2021-07-23", "float4_value": 0, "float8_value": 0, "int2_value": 0, "int4_value": 0, "int8_value": 0,  "numeric_value": 0, "text_value": "string", "timestamp_value": "2021-07-23T02:38:24.963000", "timestamptz_value": "2021-07-23T02:38:24.963000+00:00", "varchar_value": "string"},{  "char_value": "string    ", "date_value": "2021-07-23", "float4_value": 0, "float8_value": 0, "int2_value": 0, "int4_value": 0, "int8_value": 0, "numeric_value": 0, "text_value": "string", "timestamp_value": "2021-07-23T02:38:24.963000", "timestamptz_value": "2021-07-23T02:38:24.963000+00:00", "varchar_value": "string"} ] '''
    data_dict = json.loads(data)
    response = client.post('/test', headers=headers, data=data)
    assert response.status_code == 201
    response_result = response.json()
    for index, value in enumerate(data_dict):
        res_result_by_index = response_result[index]
        for k, v in value.items():
            assert res_result_by_index[k] == v


def test_update_one_data():
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }
    data = '{"float4_value": 0, "int2_value": 0, "int4_value": 0 }'
    response = client.post('/test_2', headers=headers, data=data)
    assert response.status_code == 201
    create_response = response.json()
    created_primary_key = create_response['primary_key']
    update_data = {"bool_value": False, "char_value": "string_u  ", "date_value": "2022-07-24", "float4_value": 10.50,
                   "float8_value": 10.5, "int2_value": 10, "int4_value": 10, "int8_value": 10,
                   "numeric_value": 10,
                   "text_value": "string_update",
                   "timestamp_value": "2022-07-24T02:54:53.285000",
                   "timestamptz_value": "2022-07-24T02:54:53.285000+00:00", "varchar_value": "string",
                   "time_value": "18:19:18", "timetz_value": "18:19:18+00:00"}
    query_param = urlencode(update_data)
    response = client.put(f'/test/{created_primary_key}?{query_param}', data=json.dumps(update_data))
    update_data["bool_value"] = False
    response_data = response.json()
    assert response_data
    for i in update_data:
        assert response_data[i] == update_data[i]


def test_create_many_data():
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }

    data =  [{"char_value": "string", "date_value": "2021-07-24", "float4_value": 0,
                        "float8_value": 0, "int2_value": 0, "int4_value": 0, "int8_value": 0,
                        "numeric_value": 0, "text_value": "string",
                        "timestamp_value": "2021-07-24T02:54:53.285", "timestamptz_value": "2021-07-24T02:54:53.285Z",
                        "varchar_value": "string",
                        "time_value": "18:18:18", "timetz_value": "18:18:18+00:00"},

                       {"char_value": "string", "date_value": "2021-07-24", "float4_value": 0,
                        "float8_value": 0, "int2_value": 0, "int4_value": 0, "int8_value": 0,
                        "numeric_value": 0, "text_value": "string",
                        "time_value": "18:18:18",
                        "timestamp_value": "2021-07-24T02:54:53.285",
                        "timestamptz_value": "2021-07-24T02:54:53.285Z",
                        "varchar_value": "string",
                        "timetz_value": "18:18:18+00:00"},

                       {"char_value": "string", "date_value": "2021-07-24", "float4_value": 0,
                        "float8_value": 0, "int2_value": 0, "int4_value": 0, "int8_value": 0,
                        "numeric_value": 0, "text_value": "string",
                        "timestamp_value": "2021-07-24T02:54:53.285",
                        "timestamptz_value": "2021-07-24T02:54:53.285Z",
                        "varchar_value": "string",
                        "time_value": "18:18:18",
                        "timetz_value": "18:18:18+00:00"},
                       ]

    response = client.post('/test', headers=headers, data=json.dumps(data))
    assert response.status_code == 201
    insert_response_data = response.json()

    primary_key_list = [i['primary_key'] for i in insert_response_data]
    params = {"bool_value____list": False,
              "char_value____str": 'string%',
              "char_value____str_____matching_pattern": 'case_sensitive',
              "date_value____from": "2021-07-22",
              "date_value____to": "2021-07-25",
              "float4_value____from": -1,
              "float4_value____to": 2,
              "float4_value____list": 0,
              "float8_value____from": -1,
              "float8_value____to": 2,
              "float8_value____list": 0,
              "int2_value____from": -1,
              "int2_value____to": 9,
              "int2_value____list": 0,
              "int4_value____from": -1,
              "int4_value____to": 9,
              "int4_value____list": 0,
              "int8_value____from": -1,
              "int8_value____to": 9,
              "int8_value____list": 0,
              "interval_value____from": -1,
              "interval_value____to": 9,
              "interval_value____list": 0,
              "numeric_value____from": -1,
              "numeric_value____to": 9,
              "numeric_value____list": 0,
              "text_value____list": "string",
              "time_value____from": '18:18:18',
              "time_value____to": '18:18:18',
              "time_value____list": '18:18:18',
              "timestamp_value_value____from": "2021-07-24T02:54:53.285",
              "timestamp_value_value____to": "2021-07-24T02:54:53.285",
              "timestamp_value_value____list": "2021-07-24T02:54:53.285",
              "timestamptz_value_value____from": "2021-07-24T02:54:53.285Z",
              "timestamptz_value_value____to": "2021-07-24T02:54:53.285Z",
              "timestamptz_value_value____list": "2021-07-24T02:54:53.285Z",
              "time_value____from": '18:18:18+00:00',
              "time_value____to": '18:18:18+00:00',
              "time_value____list": '18:18:18+00:00',
              "varchar_value____str": 'string',
              "varchar_value____str_____matching_pattern": 'case_sensitive',
              "varchar_value____list": 'string',
              }
    from urllib.parse import urlencode
    query_string = urlencode(
        params) + f'&primary_key____list={primary_key_list[0]}&primary_key____list={primary_key_list[1]}&primary_key____list={primary_key_list[2]}'
    update_data = {"bool_value": False, "char_value": "string_u  ", "date_value": "2022-07-24", "float4_value": 10.50,
                   "float8_value": 10.5, "int2_value": 10, "int4_value": 10, "int8_value": 10,
                   "numeric_value": 10,
                   "text_value": "string_update",
                   "timestamp_value": "2022-07-24T02:54:53.285000",
                   "timestamptz_value": "2022-07-24T02:54:53.285000+00:00",
                   "varchar_value": "string",
                   "time_value": "18:19:18", "timetz_value": "18:19:18+00:00"}
    response = client.put(f'/test?{query_string}', data=json.dumps(update_data))
    update_data["bool_value"] = False
    response_data = response.json()
    assert len(response_data) == 3
    for k in response_data:
        for i in update_data:
            assert k[i] == update_data[i]


def test_patch_one_data():
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }

    data = [
        {"char_value": "string", "date_value": "2021-07-24", "float4_value": 0,
         "float8_value": 0, "int2_value": 0, "int4_value": 0, "int8_value": 0,
         "numeric_value": 0, "text_value": "string",
         "timestamp_value": "2021-07-24T02:54:53.285",
         "timestamptz_value": "2021-07-24T02:54:53.285Z", "varchar_value": "string",
         "time_value": "18:18:18",
         "timetz_value": "18:18:18+00:00"},
    ]

    response = client.post('/test', headers=headers, data=json.dumps(data))
    assert response.status_code == 201
    insert_response_data = response.json()

    primary_key, = [i['primary_key'] for i in insert_response_data]
    params = {"bool_value____list": False,
              "char_value____str": 'string%',
              "char_value____str_____matching_pattern": 'case_sensitive',
              "date_value____from": "2021-07-22",
              "date_value____to": "2021-07-25",
              "float4_value____from": -1,
              "float4_value____to": 2,
              "float4_value____list": 0,
              "float8_value____from": -1,
              "float8_value____to": 2,
              "float8_value____list": 0,
              "int2_value____from": -1,
              "int2_value____to": 9,
              "int2_value____list": 0,
              "int4_value____from": -1,
              "int4_value____to": 9,
              "int4_value____list": 0,
              "int8_value____from": -1,
              "int8_value____to": 9,
              "int8_value____list": 0,
              "interval_value____from": -1,
              "interval_value____to": 9,
              "interval_value____list": 0,
              "numeric_value____from": -1,
              "numeric_value____to": 9,
              "numeric_value____list": 0,
              "text_value____list": "string",
              "time_value____from": '18:18:18',
              "time_value____to": '18:18:18',
              "time_value____list": '18:18:18',
              "timestamp_value_value____from": "2021-07-24T02:54:53.285",
              "timestamp_value_value____to": "2021-07-24T02:54:53.285",
              "timestamp_value_value____list": "2021-07-24T02:54:53.285",
              "timestamptz_value_value____from": "2021-07-24T02:54:53.285Z",
              "timestamptz_value_value____to": "2021-07-24T02:54:53.285Z",
              "timestamptz_value_value____list": "2021-07-24T02:54:53.285Z",
              "time_value____from": '18:18:18+00:00',
              "time_value____to": '18:18:18+00:00',
              "time_value____list": '18:18:18+00:00',
              "varchar_value____str": 'string',
              "varchar_value____str_____matching_pattern": 'case_sensitive',
              "varchar_value____list": 'string',
              }
    from urllib.parse import urlencode
    query_string = urlencode(params)
    update_data = {"bool_value": False}
    response = client.patch(f'/test/{primary_key}?{query_string}', data=json.dumps(update_data))
    response_data = response.json()
    assert response_data
    for i in update_data:
        assert response_data[i] == update_data[i]
    params['bool_value____list'] = False
    query_string = urlencode(params)
    update_data = {"char_value": "string_u  "}
    response = client.patch(f'/test/{primary_key}?{query_string}', data=json.dumps(update_data))
    response_data = response.json()
    assert response_data
    for i in update_data:
        assert response_data[i] == update_data[i]
    params['char_value____str'] = "string_u  "
    query_string = urlencode(params)
    update_data = {"date_value": "2022-07-24"}
    response = client.patch(f'/test/{primary_key}?{query_string}', data=json.dumps(update_data))
    response_data = response.json()
    assert response_data
    for i in update_data:
        assert response_data[i] == update_data[i]
    params['date_value____from'] = "2022-07-23"
    params['date_value____to'] = "2022-07-25"
    query_string = urlencode(params)
    update_data = {"char_value": "string_u  ", "date_value": "2022-07-24", "float4_value": 10.50,
                   "float8_value": 10.5, "int2_value": 10, "int4_value": 10, "int8_value": 10,
                   "numeric_value": 10,
                   "text_value": "string_update",
                   "timestamp_value": "2022-07-24T02:54:53.285000",
                   "timestamptz_value": "2022-07-24T02:54:53.285000+00:00", "varchar_value": "string",
                   "time_value": "18:19:18", "timetz_value": "18:19:18+00:00"}
    response = client.patch(f'/test/{primary_key}?{query_string}', data=json.dumps(update_data))
    update_data['bool_value'] = False
    response_data = response.json()
    assert response_data
    for i in update_data:
        assert response_data[i] == update_data[i]


def test_patch_many_data():
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }

    data = [{"char_value": "string", "date_value": "2021-07-24", "float4_value": 0,
             "float8_value": 0, "int2_value": 0, "int4_value": 0, "int8_value": 0,
             "numeric_value": 0, "text_value": "string",
             "timestamp_value": "2021-07-24T02:54:53.285", "timestamptz_value": "2021-07-24T02:54:53.285Z",
             "varchar_value": "string",
             "time_value": "18:18:18", "timetz_value": "18:18:18+00:00"},

            {"char_value": "string", "date_value": "2021-07-24", "float4_value": 0,
             "float8_value": 0, "int2_value": 0, "int4_value": 0, "int8_value": 0,
             "numeric_value": 0, "text_value": "string",
             "time_value": "18:18:18",
             "timestamp_value": "2021-07-24T02:54:53.285",
             "timestamptz_value": "2021-07-24T02:54:53.285Z",
             "varchar_value": "string",
             "timetz_value": "18:18:18+00:00"},

            {"char_value": "string", "date_value": "2021-07-24", "float4_value": 0,
             "float8_value": 0, "int2_value": 0, "int4_value": 0, "int8_value": 0,
             "numeric_value": 0, "text_value": "string",
             "timestamp_value": "2021-07-24T02:54:53.285",
             "timestamptz_value": "2021-07-24T02:54:53.285Z",
             "varchar_value": "string",
             "time_value": "18:18:18",
             "timetz_value": "18:18:18+00:00"},
            ]

    response = client.post('/test', headers=headers, data=json.dumps(data))
    assert response.status_code == 201
    insert_response_data = response.json()

    primary_key_list = [i['primary_key'] for i in insert_response_data]
    params = {
        "bool_value____list": False,
        "char_value____str": 'string%',
        "char_value____str_____matching_pattern": 'case_sensitive',
        "date_value____from": "2021-07-22",
        "date_value____to": "2021-07-25",
        "float4_value____from": -1,
        "float4_value____to": 2,
        "float4_value____list": 0,
        "float8_value____from": -1,
        "float8_value____to": 2,
        "float8_value____list": 0,
        "int2_value____from": -1,
        "int2_value____to": 9,
        "int2_value____list": 0,
        "int4_value____from": -1,
        "int4_value____to": 9,
        "int4_value____list": 0,
        "int8_value____from": -1,
        "int8_value____to": 9,
        "int8_value____list": 0,
        "interval_value____from": -1,
        "interval_value____to": 9,
        "interval_value____list": 0,
        "numeric_value____from": -1,
        "numeric_value____to": 9,
        "numeric_value____list": 0,
        "text_value____list": "string",
        "time_value____from": '18:18:18',
        "time_value____to": '18:18:18',
        "time_value____list": '18:18:18',
        "timestamp_value_value____from": "2021-07-24T02:54:53.285",
        "timestamp_value_value____to": "2021-07-24T02:54:53.285",
        "timestamp_value_value____list": "2021-07-24T02:54:53.285",
        "timestamptz_value_value____from": "2021-07-24T02:54:53.285Z",
        "timestamptz_value_value____to": "2021-07-24T02:54:53.285Z",
        "timestamptz_value_value____list": "2021-07-24T02:54:53.285Z",
        "time_value____from": '18:18:18+00:00',
        "time_value____to": '18:18:18+00:00',
        "time_value____list": '18:18:18+00:00',
        "varchar_value____str": 'string',
        "varchar_value____str_____matching_pattern": 'case_sensitive',
        "varchar_value____list": 'string',
    }
    from urllib.parse import urlencode
    query_string = urlencode(
        params) + f'&primary_key____list={primary_key_list[0]}&primary_key____list={primary_key_list[1]}&primary_key____list={primary_key_list[2]}'

    update_data = {"bool_value": True, "char_value": "string_u  ", "date_value": "2022-07-24",
                   "float8_value": 10.5, "int2_value": 10, "int4_value": 10,
                   "numeric_value": 10,
                   "text_value": "string_update",
                   "timestamp_value": "2022-07-24T02:54:53.285000",
                   "timestamptz_value": "2022-07-24T02:54:53.285000+00:00", "varchar_value": "string",
                   "time_value": "18:19:18", "timetz_value": "18:19:18+00:00"}
    response = client.patch(f'/test?{query_string}', data=json.dumps(update_data))
    update_data['bool_value'] = True
    response_data = response.json()
    assert len(response_data) == 3
    for k in response_data:
        for i in update_data:
            print(i)
            print(k[i])
            assert k[i] == update_data[i]


def test_delete_one_data():
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }

    data = [
        {"bool_value": True, "char_value": "string", "date_value": "2021-07-24", "float4_value": 0,
         "float8_value": 0, "int2_value": 0, "int4_value": 0, "int8_value": 0,
         "numeric_value": 0, "text_value": "string",
         "timestamp_value": "2021-07-24T02:54:53.285",
         "timestamptz_value": "2021-07-24T02:54:53.285",
         "varchar_value": "string",
         "time_value": "18:18:18",
         "timetz_value": "18:18:18+00:00"},
    ]

    response = client.post('/test', headers=headers, data=json.dumps(data))
    assert response.status_code == 201
    insert_response_data = response.json()

    primary_key, = [i['primary_key'] for i in insert_response_data]
    params = {"bool_value____list": True,
              "char_value____str": 'string%',
              "char_value____str_____matching_pattern": 'case_sensitive',
              "date_value____from": "2021-07-22",
              "date_value____to": "2021-07-25",
              "float4_value____from": -1,
              "float4_value____to": 2,
              "float4_value____list": 0,
              "float8_value____from": -1,
              "float8_value____to": 2,
              "float8_value____list": 0,
              "int2_value____from": -1,
              "int2_value____to": 9,
              "int2_value____list": 0,
              "int4_value____from": -1,
              "int4_value____to": 9,
              "int4_value____list": 0,
              "int8_value____from": -1,
              "int8_value____to": 9,
              "int8_value____list": 0,
              "interval_value____from": -1,
              "interval_value____to": 9,
              "interval_value____list": 0,
              "numeric_value____from": -1,
              "numeric_value____to": 9,
              "numeric_value____list": 0,
              "text_value____list": "string",
              "time_value____from": '18:18:18',
              "time_value____to": '18:18:18',
              "time_value____list": '18:18:18',
              "timestamp_value_value____from": "2021-07-24T02:54:53.285",
              "timestamp_value_value____to": "2021-07-24T02:54:53.285",
              "timestamp_value_value____list": "2021-07-24T02:54:53.285",
              "timestamptz_value_value____from": "2021-07-24T02:54:53.285Z",
              "timestamptz_value_value____to": "2021-07-24T02:54:53.285Z",
              "timestamptz_value_value____list": "2021-07-24T02:54:53.285Z",
              "time_value____from": '18:18:18+00:00',
              "time_value____to": '18:18:18+00:00',
              "time_value____list": '18:18:18+00:00',
              "varchar_value____str": 'string',
              "varchar_value____str_____matching_pattern": 'case_sensitive',
              "varchar_value____list": 'string',
              }
    from urllib.parse import urlencode
    query_string = urlencode(params)
    response = client.delete(f'/test/{primary_key}?{query_string}')
    assert response.status_code == 200
    assert response.headers['x-total-count'] == '1'


def test_delete_many_data():
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }

    data = [{"char_value": "string", "date_value": "2021-07-24", "float4_value": 0,
             "float8_value": 0, "int2_value": 0, "int4_value": 0, "int8_value": 0,
             "numeric_value": 0, "text_value": "string",
             "timestamp_value": "2021-07-24T02:54:53.285", "timestamptz_value": "2021-07-24T02:54:53.285Z",
             "varchar_value": "string",
             "time_value": "18:18:18", "timetz_value": "18:18:18+00:00"},

            {"char_value": "string", "date_value": "2021-07-24", "float4_value": 0,
             "float8_value": 0, "int2_value": 0, "int4_value": 0, "int8_value": 0,
             "numeric_value": 0, "text_value": "string",
             "time_value": "18:18:18",
             "timestamp_value": "2021-07-24T02:54:53.285",
             "timestamptz_value": "2021-07-24T02:54:53.285Z", "varchar_value": "string",
             "timetz_value": "18:18:18+00:00"},

            {"char_value": "string", "date_value": "2021-07-24", "float4_value": 0,
             "float8_value": 0, "int2_value": 0, "int4_value": 0, "int8_value": 0,
             "numeric_value": 0, "text_value": "string",
             "timestamp_value": "2021-07-24T02:54:53.285",
             "timestamptz_value": "2021-07-24T02:54:53.285Z", "varchar_value": "string",
             "time_value": "18:18:18",
             "timetz_value": "18:18:18+00:00"},
            ]

    response = client.post('/test', headers=headers, data=json.dumps(data))
    assert response.status_code == 201
    insert_response_data = response.json()

    primary_key_list = [i['primary_key'] for i in insert_response_data]
    params = {
        "bool_value____list": False,
        "char_value____str": 'string%',
        "char_value____str_____matching_pattern": 'case_sensitive',
        "date_value____from": "2021-07-22",
        "date_value____to": "2021-07-25",
        "float4_value____from": -1,
        "float4_value____to": 2,
        "float4_value____list": 0,
        "float8_value____from": -1,
        "float8_value____to": 2,
        "float8_value____list": 0,
        "int2_value____from": -1,
        "int2_value____to": 9,
        "int2_value____list": 0,
        "int4_value____from": -1,
        "int4_value____to": 9,
        "int4_value____list": 0,
        "int8_value____from": -1,
        "int8_value____to": 9,
        "int8_value____list": 0,
        "interval_value____from": -1,
        "interval_value____to": 9,
        "interval_value____list": 0,
        "numeric_value____from": -1,
        "numeric_value____to": 9,
        "numeric_value____list": 0,
        "text_value____list": "string",
        "time_value____from": '18:18:18',
        "time_value____to": '18:18:18',
        "time_value____list": '18:18:18',
        "timestamp_value_value____from": "2021-07-24T02:54:53.285",
        "timestamp_value_value____to": "2021-07-24T02:54:53.285",
        "timestamp_value_value____list": "2021-07-24T02:54:53.285",
        "timestamptz_value_value____from": "2021-07-24T02:54:53.285Z",
        "timestamptz_value_value____to": "2021-07-24T02:54:53.285Z",
        "timestamptz_value_value____list": "2021-07-24T02:54:53.285Z",
        "time_value____from": '18:18:18+00:00',
        "time_value____to": '18:18:18+00:00',
        "time_value____list": '18:18:18+00:00',
        "varchar_value____str": 'string',
        "varchar_value____str_____matching_pattern": 'case_sensitive',
        "varchar_value____list": 'string',
    }
    from urllib.parse import urlencode
    query_string = urlencode(
        params) + f'&primary_key____list={primary_key_list[0]}&primary_key____list={primary_key_list[1]}&primary_key____list={primary_key_list[2]}'

    response = client.delete(f'/test?{query_string}')
    assert response.status_code == 200
    assert response.headers['x-total-count'] == '3'


def test_post_redirect_get_data():
    headers = {
        'accept': '*/*',
        'Content-Type': 'application/json',
    }

    change = {}

    char_value_change = "test"
    date_value_change = str(date.today() - timedelta(days=1))
    float8_value_change = 0.1
    int2_value_change = 100
    int8_value_change = 100
    interval_value_change = float(5400)
    json_value_change = {"hello": "world"}
    jsonb_value_change = {"hello": "world"}
    numeric_value_change = 19.0
    text_value_change = 'hello world'
    time_value_change = '18:18:18'
    timestamp_value_change = str(datetime.utcnow().isoformat())
    timestamptz_value_change = str(datetime.utcnow().replace(tzinfo=timezone.utc).isoformat())
    timetz_value_change = '18:18:18+00:00'
    varchar_value_change = 'hello world'
    array_value_change = [1, 2, 3, 4]
    array_str__value_change = ['1', '2', '3', '4']

    change['char_value'] = char_value_change
    change['date_value'] = date_value_change
    change['float8_value'] = float8_value_change
    change['int2_value'] = int2_value_change
    change['int8_value'] = int8_value_change
    change['float4_value'] = 0.4
    change['int4_value'] = 4
    change['interval_value'] = interval_value_change
    change['json_value'] = json_value_change
    change['jsonb_value'] = jsonb_value_change
    change['numeric_value'] = numeric_value_change
    change['text_value'] = text_value_change
    change['time_value'] = time_value_change
    change['timestamp_value'] = timestamp_value_change
    change['timestamptz_value'] = timestamptz_value_change
    change['timetz_value'] = timetz_value_change
    change['varchar_value'] = varchar_value_change
    change['array_value'] = array_value_change
    change['array_str__value'] = array_str__value_change
    data_ = json.dumps(change)
    response = client.post('/test_3', headers=headers, data=data_, allow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    response_data['bool_value'] = False
    assert 'primary_key' in response_data
    # for k, v in response_data.items():
    #     if k in change:
    #         if isinstance(v, str):
    #             v = v.strip()
    #         response_ = json.dumps(v).strip()
    #         request_ = json.dumps(change[k]).strip()
    #         assert request_ == response_
    return response_data


def test_create_one():
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }
    data = '{"float4_value": 0, "int2_value": 0, "int4_value": 10 }'
    response = client.post('/test_2', headers=headers, data=data)
    assert response.status_code == 201
    create_response = response.json()
    updated_data = {}
    for k, v in create_response.items():
        if k not in data:
            updated_data[k] = v
    updated_data['numeric_value'] = 100

