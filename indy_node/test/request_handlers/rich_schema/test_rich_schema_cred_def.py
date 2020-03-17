import copy
import json

import pytest

from indy_common.constants import RS_CONTENT, ENDORSER, RS_ID, RS_CRED_DEF_SCHEMA, RS_CRED_DEF_MAPPING
from indy_node.server.request_handlers.domain_req_handlers.rich_schema.rich_schema_cred_def_handler import \
    RichSchemaCredDefHandler
from indy_node.server.request_handlers.domain_req_handlers.rich_schema.rich_schema_handler import RichSchemaHandler
from indy_node.server.request_handlers.domain_req_handlers.rich_schema.rich_schema_mapping_handler import \
    RichSchemaMappingHandler
from indy_node.test.request_handlers.helper import add_to_idr
from indy_node.test.request_handlers.rich_schema.helper import rich_schema_request, rich_schema_cred_def_request, \
    rich_schema_mapping_request, make_rich_schema_object_exist
from plenum.common.constants import TRUSTEE
from plenum.common.exceptions import InvalidClientRequest


@pytest.fixture()
def cred_def_req():
    return rich_schema_cred_def_request()


@pytest.fixture()
def cred_def_handler(db_manager, write_auth_req_validator):
    return RichSchemaCredDefHandler(db_manager, write_auth_req_validator)


@pytest.fixture()
def rich_schema_req():
    return rich_schema_request()


@pytest.fixture()
def rich_schema_handler(db_manager, write_auth_req_validator):
    return RichSchemaHandler(db_manager, write_auth_req_validator)


@pytest.fixture()
def mapping_req():
    return rich_schema_mapping_request()


@pytest.fixture()
def mapping_handler(db_manager, write_auth_req_validator):
    return RichSchemaMappingHandler(db_manager, write_auth_req_validator)


def test_static_validation_pass(cred_def_handler, cred_def_req):
    cred_def_handler.static_validation(cred_def_req)


@pytest.mark.parametrize('missing_field', ['signatureType', 'mapping', 'schema', 'publicKey'])
@pytest.mark.parametrize('status', ['missing', 'empty', 'none'])
def test_static_validation_no_field(cred_def_handler, cred_def_req, missing_field, status):
    content = copy.deepcopy(json.loads(cred_def_req.operation[RS_CONTENT]))
    if status == 'missing':
        content.pop(missing_field, None)
    elif status == 'empty':
        content[missing_field] = ""
    elif status == 'none':
        content[missing_field] = None
    cred_def_req.operation[RS_CONTENT] = json.dumps(content)

    with pytest.raises(InvalidClientRequest,
                       match="{} must be set".format(missing_field)):
        cred_def_handler.static_validation(cred_def_req)


def testdynamic_validation_passes(cred_def_handler, cred_def_req,
                                  rich_schema_handler, rich_schema_req,
                                  mapping_handler, mapping_req):
    add_to_idr(cred_def_handler.database_manager.idr_cache, cred_def_req.identifier, TRUSTEE)
    add_to_idr(cred_def_handler.database_manager.idr_cache, cred_def_req.endorser, ENDORSER)

    make_rich_schema_object_exist(rich_schema_handler, rich_schema_req)
    make_rich_schema_object_exist(mapping_handler, mapping_req)

    content = copy.deepcopy(json.loads(cred_def_req.operation[RS_CONTENT]))
    content[RS_CRED_DEF_SCHEMA] = rich_schema_req.operation[RS_ID]
    content[RS_CRED_DEF_MAPPING] = mapping_req.operation[RS_ID]

    cred_def_handler.dynamic_validation(cred_def_req, 0)


def test_dynamic_validation_not_existent_schema(cred_def_handler, cred_def_req):
    pass
