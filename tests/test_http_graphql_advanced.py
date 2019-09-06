#
# This source file is part of the EdgeDB open source project.
#
# Copyright 2019-present MagicStack Inc. and the EdgeDB authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


import os

from edb.testbase import http as tb


class TestGraphQLAdvanced(tb.GraphQLTestCase):
    SCHEMA_DEFAULT = os.path.join(os.path.dirname(__file__), 'schemas',
                                  'gql_inheritance.esdl')

    SETUP = os.path.join(os.path.dirname(__file__), 'schemas',
                         'gql_inheritance_setup.edgeql')

    # GraphQL queries cannot run in a transaction
    ISOLATED_METHODS = False

    def test_graphql_advanced_query_01(self):
        self.assert_graphql_query_result(r"""
            query {
                Bar {
                    __typename
                    q
                }
            }
        """, {
            'Bar': [{
                '__typename': 'BarType',
                'q': 'bar',
            }, {
                '__typename': 'Bar2Type',
                'q': 'bar2',
            }],
        }, sort=lambda x: x['q'])

    def test_graphql_advanced_query_02(self):
        self.assert_graphql_query_result(r"""
            query {
                Foo {
                    __typename
                    blah {
                        __typename
                        q
                    }
                }
            }
        """, {
            'Foo': [{
                '__typename': 'FooType',
                'blah': {
                    '__typename': 'BarType',
                    'q': 'bar',
                }
            }, {
                '__typename': 'Foo2Type',
                'blah': {
                    '__typename': 'Bar2Type',
                    'q': 'bar2',
                }
            }],
        }, sort=lambda x: x['blah']['q'])

    def test_graphql_advanced_query_03(self):
        # Foo2 must keep the target type of the link same as the base
        # type, due to limitations of GraphQL inheritance. But as long
        # as the actual target type is known, it can be explicitly
        # referenced.
        self.assert_graphql_query_result(r"""
            query {
                Foo2 {
                    blah {
                        __typename
                        ... on Bar2 {
                            q
                            w
                        }
                    }
                }
            }
        """, {
            'Foo2': [{
                'blah': {
                    '__typename': 'Bar2Type',
                    'q': 'bar2',
                    'w': 'special'
                }
            }],
        })
