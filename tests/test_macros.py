import pandas as pd
from datetime import datetime
from geotable.exceptions import GeoTableError
from geotable.macros import (
    _get_geometry_columns,
    _get_get_field_values,
    _get_load_geometry_object,
    _has_one_proj4,
    _transform_field_value)
from osgeo import ogr
from pytest import raises
from shapely.geometry import Point

from conftest import prepare_feature


def test_get_geometry_columns():
    t = pd.DataFrame([('POINT(0 0)',)], columns=['WKT'])
    assert _get_geometry_columns(t) == ['WKT']

    t = pd.DataFrame([('POINT(0 0)',)], columns=['LONGITUDE_LATITUDE_WKT'])
    assert _get_geometry_columns(t) == ['LONGITUDE_LATITUDE_WKT']

    t = pd.DataFrame([('POINT(0 0)',)], columns=['LATITUDE_LONGITUDE_WKT'])
    assert _get_geometry_columns(t) == ['LATITUDE_LONGITUDE_WKT']

    t = pd.DataFrame([(0, 0)], columns=['Longitude', 'Latitude'])
    assert _get_geometry_columns(t) == ['Longitude', 'Latitude']

    t = pd.DataFrame([(0, 0)], columns=['LON', 'LAT'])
    assert _get_geometry_columns(t) == ['LON', 'LAT']

    t = pd.DataFrame([(0, 0)], columns=['X', 'Y'])
    assert _get_geometry_columns(t) == ['X', 'Y']


def test_get_get_field_values():
    feature, field_type_by_name, field_values = prepare_feature([
        ('xyz', ogr.OFTString, 'abc'),
    ])
    f = _get_get_field_values({'xyz': None})
    assert f(feature) == field_values

    feature, field_type_by_name, field_values = prepare_feature([
        # ('binary', ogr.OFTBinary, b'\x00\x01\x02'),
        ('date', ogr.OFTDate, datetime(2000, 1, 1, 0, 0)),
        ('datetime', ogr.OFTDateTime, datetime(2000, 1, 1, 0, 0)),
        ('int', ogr.OFTInteger, 0),
        ('int_l', ogr.OFTIntegerList, [0, 1]),
        ('int64', ogr.OFTInteger64, 0),
        ('int64_l', ogr.OFTInteger64List, [0, 1]),
        ('real', ogr.OFTReal, 1.0),
        ('real_l', ogr.OFTRealList, [0.0, 1.0]),
        ('string', ogr.OFTString, 'whee'),
        ('string_l', ogr.OFTStringList, ['whee', 'hooray']),
        # ('time', ogr.OFTTime, datetime(2000, 1, 1, 0, 0)),
        # ('wstring', ogr.OFTWideString, 'whee'),
        # ('wstring_l', ogr.OFTWideStringList, ['whee', 'hooray']),
    ])
    f = _get_get_field_values(field_type_by_name)
    assert f(feature) == field_values


def test_get_load_geometry_object():
    f = _get_load_geometry_object(['x', 'y'])
    f(pd.Series({'x': 1, 'y': 2})) == Point(1, 2)

    f = _get_load_geometry_object(['longitude_latitude_wkt'])
    f(pd.Series({'longitude_latitude_wkt': 'POINT (1 2)'})) == Point(1, 2)

    f = _get_load_geometry_object(['latitude_longitude_wkt'])
    f(pd.Series({'latitude_longitude_wkt': 'POINT (2 1)'})) == Point(1, 2)

    with raises(GeoTableError):
        _get_load_geometry_object(['x'])


def test_has_one_proj4():
    assert _has_one_proj4(pd.DataFrame()) is False


def test_transform_field_value():
    assert _transform_field_value('x', ogr.OFTDate) == 'x'
