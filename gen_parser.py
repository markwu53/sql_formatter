from base import *
from sql_lexer import lexer

parser_data = dict()

id = lambda d: d

def get_token(p):
    tokens = parser_data["tokens"]
    if p == len(tokens):
        return -1, []
    return p+1, [tokens[p]]

def symbol_bare(s):
    def good(d):
        (t,v), = d
        return t == "symbol" and v == s
    return check(get_token, good)

keywords_not_identifier = [
    "select",
    "from",
    "where",
    "group",
    "by",
    "order",
    "in",
    "between",
    "and",
    "on",
    "or",
    "when",
    "then",
    "else",
    "case",
    "cast",
    "partition",
    "over",
    "having",
    "not",
    "join",
    "asc",
    "desc",
    "union",
    "all",
    "except",
    "intersect",
    "into",
    "set",
    "exec",
    "execute",
    "if",
    "end",
    "create",
    "return",
    "update",
    "declare",
    "option",
    "pivot",
    "grouping",
    "try",
    "catch",
    "merge",
    "while",
    "begin",
    ]
token_identifier_all = check(get_token, lambda d: d[0][0] == "identifier")
token_identifier = check(get_token, lambda d: d[0][0] == "identifier" and d[0][1].lower() not in keywords_not_identifier)
token_string = check(get_token, lambda d: d[0][0] == "string")
token_number = check(get_token, lambda d: d[0][0] == "number")
token_quoted = check(get_token, lambda d: d[0][0] == "quoted")
token_bracketed = check(get_token, lambda d: d[0][0] == "bracketed")
token_comment = check(get_token, lambda d: d[0][0] in ["block_comment", "line_comment"])

def keyword(k):
    def good(d):
        t,v = d[0]
        return k.upper() == v.upper()
    def proc_keyword(d):
        t,v = d[0]
        return [("keyword", v)]
    return proc(check(token_identifier_all, good), proc_keyword)

#default_proc_functions
from default_udf import *

#user defined proc functions
from udf import *

comments = proc(more(token_comment), proc_comments)

def symbol(s):
    return sequential(optional(comments), symbol_bare(s))

#rule_functions
def create_procedure(p): return proc(sequential(optional(comments), create_procedure_sig, sql_statements, optional(comments)), proc_create_procedure)(p)
def create_function(p): return proc(sequential(optional(comments), create_function_sig, sql_statements, optional(comments)), proc_create_function)(p)
def sql_statements(p): return proc(sequential(optional(comments), more(sql_statement), optional(comments)), proc_sql_statements)(p)
def create_procedure_sig(p): return proc(sequential(optional(comments), create_procedure_head, optional(sp_parameter_list), keyword("AS"), optional(comments)), proc_create_procedure_sig)(p)
def create_procedure_head(p): return proc(sequential(optional(comments), keyword("CREATE"), procedure, procedure_name, optional(comments)), proc_create_procedure_head)(p)
def procedure_name(p): return proc(sequential(optional(comments), qualified_name, optional(comments)), proc_procedure_name)(p)
def sp_parameter_list(p): return proc(parallel(sequential(optional(comments), sp_parameter_list_1, optional(comments)), sequential(optional(comments), sp_parameter_list_group, optional(comments))), proc_sp_parameter_list)(p)
def sp_parameter_list_group(p): return proc(sequential(optional(comments), symbol("("), sp_parameter_list_1, symbol(")"), optional(comments)), proc_sp_parameter_list_group)(p)
def sp_parameter_list_1(p): return proc(sequential(optional(comments), sp_parameter, star(sp_next_parameter), optional(comments)), proc_sp_parameter_list_1)(p)
def sp_next_parameter(p): return proc(sequential(optional(comments), symbol(","), sp_parameter, optional(comments)), proc_sp_next_parameter)(p)
def sp_parameter(p): return proc(sequential(optional(comments), sql_variable, data_type, optional(variable_init), optional(comments)), proc_sp_parameter)(p)
def procedure(p): return proc(parallel(sequential(optional(comments), keyword("PROCEDURE"), optional(comments)), sequential(optional(comments), keyword("PROC"), optional(comments))), proc_procedure)(p)
def create_function_sig(p): return proc(sequential(optional(comments), create_function_head, optional(sp_parameter_list), optional(return_type), optional(keyword("AS")), optional(comments)), proc_create_function_sig)(p)
def create_function_head(p): return proc(sequential(optional(comments), keyword("CREATE"), function_word, function_name, optional(comments)), proc_create_function_head)(p)
def function_word(p): return proc(parallel(sequential(optional(comments), keyword("FUNCTION"), optional(comments)), sequential(optional(comments), keyword("FUNC"), optional(comments))), proc_function_word)(p)
def function_name(p): return proc(sequential(optional(comments), qualified_name, optional(comments)), proc_function_name)(p)
def return_type(p): return proc(sequential(optional(comments), keyword("RETURNS"), qualified_item, optional(comments)), proc_return_type)(p)
def sql_statement(p): return proc(parallel(sequential(optional(comments), sql_statement_bare, optional(symbol(";")), optional(comments)), sequential(optional(comments), symbol(";"), optional(comments))), proc_sql_statement)(p)
def sql_statement_bare(p): return proc(parallel(sequential(optional(comments), query_statement, optional(comments)), sequential(optional(comments), declare_statement, optional(comments)), sequential(optional(comments), return_statement, optional(comments)), sequential(optional(comments), while_statement, optional(comments)), sequential(optional(comments), break_statement, optional(comments)), sequential(optional(comments), continue_statement, optional(comments)), sequential(optional(comments), set_statement, optional(comments)), sequential(optional(comments), create_table_statement, optional(comments)), sequential(optional(comments), create_index_statement, optional(comments)), sequential(optional(comments), set_on, optional(comments)), sequential(optional(comments), begin_try_block, optional(comments)), sequential(optional(comments), begin_end_block, optional(comments)), sequential(optional(comments), if_statement, optional(comments)), sequential(optional(comments), exec_statement, optional(comments)), sequential(optional(comments), drop_statement, optional(comments)), sequential(optional(comments), truncate_statement, optional(comments)), sequential(optional(comments), raiserror_statement, optional(comments))), proc_sql_statement_bare)(p)
def merge_statement(p): return proc(sequential(optional(comments), merge_1, more(merge_when), optional(comments)), proc_merge_statement)(p)
def merge_1(p): return proc(sequential(optional(comments), keyword("MERGE"), table_name, optional(as_table_alias), keyword("USING"), one_table_source, optional(as_table_alias), keyword("ON"), boolean_expression, optional(comments)), proc_merge_1)(p)
def create_table_statement(p): return proc(sequential(optional(comments), keyword("CREATE"), keyword("TABLE"), table_or_view_name, column_full_spec, optional(comments)), proc_create_table_statement)(p)
def table_or_view_name(p): return proc(sequential(optional(comments), qualified_name, optional(comments)), proc_table_or_view_name)(p)
def create_index_statement(p): return proc(sequential(optional(comments), keyword("CREATE"), optional(index_type), keyword("INDEX"), qualified_name, keyword("ON"), qualified_name, paren_list_1, optional(comments)), proc_create_index_statement)(p)
def index_type(p): return proc(parallel(sequential(optional(comments), keyword("CLUSTERED"), optional(comments)), sequential(optional(comments), keyword("NONCLUSTERED"), optional(comments))), proc_index_type)(p)
def column_full_spec(p): return proc(sequential(optional(comments), symbol("("), one_column_full_spec, star(next_column_full_spec), symbol(")"), optional(comments)), proc_column_full_spec)(p)
def one_column_full_spec(p): return proc(sequential(optional(comments), more(column_spec_item), optional(comments)), proc_one_column_full_spec)(p)
def column_spec_item(p): return proc(parallel(sequential(optional(comments), optional(keyword("NOT")), keyword("NULL"), optional(comments)), sequential(optional(comments), qualified_item, optional(comments))), proc_column_spec_item)(p)
def next_column_full_spec(p): return proc(sequential(optional(comments), symbol(","), one_column_full_spec, optional(comments)), proc_next_column_full_spec)(p)
def merge_when(p): return proc(sequential(optional(comments), merge_when_1, merge_action, optional(comments)), proc_merge_when)(p)
def merge_when_1(p): return proc(sequential(optional(comments), keyword("WHEN"), optional(keyword("NOT")), keyword("MATCHED"), optional(matched_by), optional(merge_condition), keyword("THEN"), optional(comments)), proc_merge_when_1)(p)
def matched_by(p): return proc(parallel(sequential(optional(comments), keyword("BY"), keyword("SOURCE"), optional(comments)), sequential(optional(comments), keyword("BY"), keyword("TARGET"), optional(comments))), proc_matched_by)(p)
def merge_condition(p): return proc(sequential(optional(comments), keyword("AND"), boolean_expression, optional(comments)), proc_merge_condition)(p)
def merge_action(p): return proc(parallel(sequential(optional(comments), keyword("INSERT"), paren_list_3, merge_insert_values, optional(comments)), sequential(optional(comments), keyword("UPDATE"), set_update_list, optional(comments))), proc_merge_action)(p)
def merge_insert_values(p): return proc(sequential(optional(comments), keyword("VALUES"), paren_list_2, optional(comments)), proc_merge_insert_values)(p)
def set_update_list(p): return proc(sequential(optional(comments), keyword("SET"), update_one, star(update_next), optional(comments)), proc_set_update_list)(p)
def paren_list_1(p): return proc(sequential(optional(comments), symbol("("), expression, star(next_expression), symbol(")"), optional(comments)), proc_paren_list_1)(p)
def paren_list_2(p): return proc(sequential(optional(comments), symbol("("), expression, star(next_expression), symbol(")"), optional(comments)), proc_paren_list_2)(p)
def paren_list_3(p): return proc(sequential(optional(comments), symbol("("), expression, star(next_expression), symbol(")"), optional(comments)), proc_paren_list_3)(p)
def while_statement(p): return proc(sequential(optional(comments), while_condition, sql_statement, optional(comments)), proc_while_statement)(p)
def while_condition(p): return proc(sequential(optional(comments), keyword("WHILE"), boolean_expression, optional(comments)), proc_while_condition)(p)
def break_statement(p): return proc(sequential(optional(comments), keyword("BREAK"), optional(comments)), proc_break_statement)(p)
def continue_statement(p): return proc(sequential(optional(comments), keyword("CONTINUE"), optional(comments)), proc_continue_statement)(p)
def truncate_statement(p): return proc(sequential(optional(comments), truncate_word, keyword("TABLE"), qualified_item, optional(comments)), proc_truncate_statement)(p)
def truncate_word(p): return proc(parallel(sequential(optional(comments), keyword("TRUNCATE"), optional(comments)), sequential(optional(comments), keyword("TRUNC"), optional(comments))), proc_truncate_word)(p)
def raiserror_statement(p): return proc(sequential(optional(comments), keyword("RAISERROR"), function_parameters, optional(comments)), proc_raiserror_statement)(p)
def begin_end_block(p): return proc(sequential(optional(comments), keyword("BEGIN"), more(sql_statement), keyword("END"), optional(comments)), proc_begin_end_block)(p)
def begin_try_block(p): return proc(sequential(optional(comments), begin_try, more(sql_statement), end_try, begin_catch, more(sql_statement), end_catch, optional(comments)), proc_begin_try_block)(p)
def begin_try(p): return proc(sequential(optional(comments), keyword("BEGIN"), keyword("TRY"), optional(comments)), proc_begin_try)(p)
def end_try(p): return proc(sequential(optional(comments), keyword("END"), keyword("TRY"), optional(comments)), proc_end_try)(p)
def begin_catch(p): return proc(sequential(optional(comments), keyword("BEGIN"), keyword("CATCH"), optional(comments)), proc_begin_catch)(p)
def end_catch(p): return proc(sequential(optional(comments), keyword("END"), keyword("CATCH"), optional(comments)), proc_end_catch)(p)
def query_statement(p): return proc(sequential(optional(comments), optional(with_cte), query_statement_type, optional(comments)), proc_query_statement)(p)
def query_statement_type(p): return proc(parallel(sequential(optional(comments), insert_statement, optional(comments)), sequential(optional(comments), update_statement, optional(comments)), sequential(optional(comments), delete_statement, optional(comments)), sequential(optional(comments), select_statement, optional(comments)), sequential(optional(comments), merge_statement, optional(comments))), proc_query_statement_type)(p)
def insert_statement(p): return proc(sequential(optional(comments), insert_into_table_name, optional(paren_list_3), insert_value, optional(comments)), proc_insert_statement)(p)
def insert_value(p): return proc(parallel(sequential(optional(comments), value_clause, optional(comments)), sequential(optional(comments), insert_query, optional(comments))), proc_insert_value)(p)
def value_clause(p): return proc(sequential(optional(comments), keyword("VALUES"), value_one, star(value_next), optional(comments)), proc_value_clause)(p)
def value_next(p): return proc(sequential(optional(comments), symbol(","), value_one, optional(comments)), proc_value_next)(p)
def value_one(p): return proc(sequential(optional(comments), paren_list_1, optional(comments)), proc_value_one)(p)
def insert_query(p): return proc(sequential(optional(comments), query_expression, optional(order_by_clause), optional(comments)), proc_insert_query)(p)
def insert_into_table_name(p): return proc(sequential(optional(comments), keyword("INSERT"), optional(keyword("INTO")), insert_table, optional(comments)), proc_insert_into_table_name)(p)
def insert_table(p): return proc(sequential(optional(comments), qualified_name, optional(comments)), proc_insert_table)(p)
def update_statement(p): return proc(sequential(optional(comments), keyword("UPDATE"), table_name, optional(as_table_alias), keyword("SET"), update_list, optional(from_clause), optional(where_clause), optional(group_by), optional(having_clause), optional(comments)), proc_update_statement)(p)
def update_list(p): return proc(sequential(optional(comments), update_one, star(update_next), optional(comments)), proc_update_list)(p)
def update_one(p): return proc(sequential(optional(comments), qualified_item, symbol("="), expression, optional(comments)), proc_update_one)(p)
def update_next(p): return proc(sequential(optional(comments), symbol(","), update_one, optional(comments)), proc_update_next)(p)
def delete_statement(p): return proc(sequential(optional(comments), keyword("DELETE"), optional(from_clause), optional(where_clause), optional(group_by), optional(having_clause), optional(comments)), proc_delete_statement)(p)
def declare_statement(p): return proc(parallel(sequential(optional(comments), declare_table, optional(comments)), sequential(optional(comments), keyword("DECLARE"), declare_one_var, star(declare_next_var), optional(comments))), proc_declare_statement)(p)
def declare_table(p): return proc(sequential(optional(comments), keyword("DECLARE"), sql_variable, keyword("TABLE"), symbol("("), declare_table_column, star(declare_table_next_column), symbol(")"), optional(comments)), proc_declare_table)(p)
def declare_table_next_column(p): return proc(sequential(optional(comments), symbol(","), declare_table_column, optional(comments)), proc_declare_table_next_column)(p)
def declare_table_column(p): return proc(sequential(optional(comments), qualified_item, qualified_item, star(qualified_item), optional(comments)), proc_declare_table_column)(p)
def declare_one_var(p): return proc(sequential(optional(comments), sql_variable, data_type, optional(variable_init), optional(comments)), proc_declare_one_var)(p)
def declare_next_var(p): return proc(sequential(optional(comments), symbol(","), declare_one_var, optional(comments)), proc_declare_next_var)(p)
def variable_init(p): return proc(sequential(optional(comments), symbol("="), expression, optional(comments)), proc_variable_init)(p)
def data_type(p): return proc(sequential(optional(comments), qualified_item, optional(comments)), proc_data_type)(p)
def set_statement(p): return proc(sequential(optional(comments), keyword("SET"), set_one_var, star(set_next_var), optional(comments)), proc_set_statement)(p)
def set_one_var(p): return proc(sequential(optional(comments), sql_variable, variable_init, optional(comments)), proc_set_one_var)(p)
def set_next_var(p): return proc(sequential(optional(comments), symbol(","), set_one_var, optional(comments)), proc_set_next_var)(p)
def set_on(p): return proc(sequential(optional(comments), keyword("SET"), set_name, on_off, optional(comments)), proc_set_on)(p)
def set_name(p): return proc(parallel(sequential(optional(comments), keyword("COUNT"), optional(comments)), sequential(optional(comments), keyword("NOCOUNT"), optional(comments)), sequential(optional(comments), keyword("IDENTITY_INSERT"), optional(qualified_item), optional(comments))), proc_set_name)(p)
def on_off(p): return proc(parallel(sequential(optional(comments), keyword("ON"), optional(comments)), sequential(optional(comments), keyword("OFF"), optional(comments))), proc_on_off)(p)
def return_statement(p): return proc(sequential(optional(comments), keyword("RETURN"), optional(expression), optional(comments)), proc_return_statement)(p)
def if_statement(p): return proc(sequential(optional(comments), if_boolean_expression, sql_statement, optional(if_statement_else), optional(comments)), proc_if_statement)(p)
def if_boolean_expression(p): return proc(sequential(optional(comments), keyword("IF"), boolean_expression, optional(comments)), proc_if_boolean_expression)(p)
def if_statement_else(p): return proc(sequential(optional(comments), keyword("ELSE"), sql_statement, optional(comments)), proc_if_statement_else)(p)
def exec_statement(p): return proc(sequential(optional(comments), exec_word, expression, optional(exec_parameters), optional(comments)), proc_exec_statement)(p)
def exec_word(p): return proc(parallel(sequential(optional(comments), keyword("EXEC"), optional(comments)), sequential(optional(comments), keyword("EXECUTE"), optional(comments))), proc_exec_word)(p)
def exec_parameters(p): return proc(sequential(optional(comments), exec_one_para, star(exec_next_para), optional(comments)), proc_exec_parameters)(p)
def exec_one_para(p): return proc(sequential(optional(comments), optional(exec_parameter_name_equal), expression, optional(comments)), proc_exec_one_para)(p)
def exec_parameter_name_equal(p): return proc(sequential(optional(comments), sql_variable, symbol("="), optional(comments)), proc_exec_parameter_name_equal)(p)
def exec_next_para(p): return proc(sequential(optional(comments), symbol(","), exec_one_para, optional(comments)), proc_exec_next_para)(p)
def drop_statement(p): return proc(sequential(optional(comments), keyword("DROP"), drop_something, optional(comments)), proc_drop_statement)(p)
def drop_something(p): return proc(parallel(sequential(optional(comments), keyword("TABLE"), table_or_view_name, optional(comments)), sequential(optional(comments), keyword("VIEW"), table_or_view_name, optional(comments))), proc_drop_something)(p)
def select_statement(p): return proc(sequential(optional(comments), query_expression, optional(comments)), proc_select_statement)(p)
def next_cte(p): return proc(sequential(optional(comments), symbol(","), cte, optional(comments)), proc_next_cte)(p)
def with_cte(p): return proc(sequential(optional(comments), keyword("WITH"), cte, star(next_cte), optional(comments)), proc_with_cte)(p)
def cte(p): return proc(sequential(optional(comments), cte_name, optional(paren_list_3), keyword("AS"), query_expression_group, optional(comments)), proc_cte)(p)
def cte_name(p): return proc(sequential(optional(comments), name, optional(comments)), proc_cte_name)(p)
def query_expression(p): return proc(sequential(optional(comments), query_expression_one, star(next_query_expression), optional(comments)), proc_query_expression)(p)
def query_expression_one(p): return proc(parallel(sequential(optional(comments), query_specification, optional(comments)), sequential(optional(comments), value_as_table, optional(comments)), sequential(optional(comments), query_expression_group, optional(comments))), proc_query_expression_one)(p)
def query_set_op(p): return proc(parallel(sequential(optional(comments), keyword("UNION"), optional(keyword("ALL")), optional(comments)), sequential(optional(comments), keyword("EXCEPT"), optional(comments)), sequential(optional(comments), keyword("INTERSECT"), optional(comments))), proc_query_set_op)(p)
def next_query_expression(p): return proc(sequential(optional(comments), query_set_op, query_expression_one, optional(comments)), proc_next_query_expression)(p)
def query_expression_group(p): return proc(sequential(optional(comments), symbol("("), subquery_expression, symbol(")"), optional(comments)), proc_query_expression_group)(p)
def subquery_expression(p): return proc(sequential(optional(comments), query_expression, optional(comments)), proc_subquery_expression)(p)
def value_as_table(p): return proc(sequential(optional(comments), value_clause, optional(comments)), proc_value_as_table)(p)
def query_specification(p): return proc(sequential(optional(comments), select_distinct_top, select_list, optional(query_into), optional(from_clause), optional(where_clause), optional(group_by), optional(having_clause), optional(order_by_clause), optional(for_clause), optional(option_clause), optional(comments)), proc_query_specification)(p)
def select_distinct_top(p): return proc(sequential(optional(comments), keyword("SELECT"), optional(query_distinct), optional(query_top), optional(comments)), proc_select_distinct_top)(p)
def query_distinct(p): return proc(parallel(sequential(optional(comments), keyword("ALL"), optional(comments)), sequential(optional(comments), keyword("DISTINCT"), optional(comments))), proc_query_distinct)(p)
def query_top(p): return proc(sequential(optional(comments), keyword("TOP"), expression, optional(keyword("PERCENT")), optional(comments)), proc_query_top)(p)
def query_into(p): return proc(sequential(optional(comments), keyword("INTO"), new_table, optional(comments)), proc_query_into)(p)
def where_clause(p): return proc(sequential(optional(comments), keyword("WHERE"), search_condition, optional(comments)), proc_where_clause)(p)
def having_clause(p): return proc(sequential(optional(comments), keyword("HAVING"), search_condition, optional(comments)), proc_having_clause)(p)
def new_table(p): return proc(sequential(optional(comments), qualified_item, optional(comments)), proc_new_table)(p)
def qualified_item(p): return proc(sequential(optional(comments), optional(scope_qualified), name_or_function, optional(comments)), proc_qualified_item)(p)
def qualified_name(p): return proc(sequential(optional(comments), optional(scope_qualified), name, optional(comments)), proc_qualified_name)(p)
def scope_qualified(p): return proc(sequential(optional(comments), scope_first, star(scope_next), optional(comments)), proc_scope_qualified)(p)
def scope_first(p): return proc(sequential(optional(comments), name_or_function, qualifier, optional(comments)), proc_scope_first)(p)
def scope_next(p): return proc(sequential(optional(comments), optional(name_or_function), qualifier, optional(comments)), proc_scope_next)(p)
def name_or_function(p): return proc(sequential(optional(comments), name, optional(function_parameters), optional(comments)), proc_name_or_function)(p)
def qualifier(p): return proc(sequential(optional(comments), symbol("."), optional(comments)), proc_qualifier)(p)
def bare_name(p): return proc(parallel(sequential(optional(comments), token_identifier, optional(comments)), sequential(optional(comments), token_quoted, optional(comments)), sequential(optional(comments), token_bracketed, optional(comments))), proc_bare_name)(p)
def name(p): return proc(parallel(sequential(optional(comments), bare_name, optional(comments)), sequential(optional(comments), symbol("@"), bare_name, optional(comments)), sequential(optional(comments), symbol("#"), bare_name, optional(comments))), proc_name)(p)
def function_parameters(p): return proc(sequential(optional(comments), symbol("("), optional(parameter_list), symbol(")"), optional(comments)), proc_function_parameters)(p)
def parameter_list(p): return proc(sequential(optional(comments), parameter, star(next_parameter), optional(comments)), proc_parameter_list)(p)
def next_parameter(p): return proc(sequential(optional(comments), symbol(","), parameter, optional(comments)), proc_next_parameter)(p)
def parameter(p): return proc(sequential(optional(comments), optional(para_qualifier), expression, optional(comments)), proc_parameter)(p)
def para_qualifier(p): return proc(sequential(optional(comments), keyword("DISTINCT"), optional(comments)), proc_para_qualifier)(p)
def for_clause(p): return proc(sequential(optional(comments), for_xml, optional(comments)), proc_for_clause)(p)
def for_xml(p): return proc(sequential(optional(comments), keyword("FOR"), keyword("XML"), for_xml_branch, optional(comments)), proc_for_xml)(p)
def for_xml_branch(p): return proc(parallel(sequential(optional(comments), for_xml_raw, optional(comments)), sequential(optional(comments), for_xml_path, optional(comments))), proc_for_xml_branch)(p)
def for_xml_raw(p): return proc(sequential(optional(comments), raw_or_auto, optional(xml_element), optional(xml_option), optional(comments)), proc_for_xml_raw)(p)
def raw_or_auto(p): return proc(parallel(sequential(optional(comments), keyword("RAW"), optional(comments)), sequential(optional(comments), keyword("AUTO"), optional(comments))), proc_raw_or_auto)(p)
def xml_element(p): return proc(sequential(optional(comments), symbol("("), token_string, symbol(")"), optional(comments)), proc_xml_element)(p)
def xml_option(p): return proc(sequential(optional(comments), symbol(","), keyword("ELEMENTS"), optional(comments)), proc_xml_option)(p)
def for_xml_path(p): return proc(sequential(optional(comments), keyword("PATH"), optional(xml_element), optional(xml_option), optional(comments)), proc_for_xml_path)(p)
def option_clause(p): return proc(sequential(optional(comments), keyword("OPTION"), symbol("("), option_one, star(option_next), symbol(")"), optional(comments)), proc_option_clause)(p)
def option_one(p): return proc(sequential(optional(comments), more(expression), optional(comments)), proc_option_one)(p)
def option_next(p): return proc(sequential(optional(comments), symbol(","), option_one, optional(comments)), proc_option_next)(p)
def select_list(p): return proc(sequential(optional(comments), select_one_column_1, star(select_next_column), optional(comments)), proc_select_list)(p)
def select_next_column(p): return proc(sequential(optional(comments), symbol(","), select_one_column_1, optional(comments)), proc_select_next_column)(p)
def select_one_column_1(p): return proc(sequential(optional(comments), optional(sql_variable_assign), select_one_column, optional(comments)), proc_select_one_column_1)(p)
def sql_variable_assign(p): return proc(sequential(optional(comments), sql_variable, symbol("="), optional(comments)), proc_sql_variable_assign)(p)
def select_one_column(p): return proc(parallel(sequential(optional(comments), symbol("*"), optional(comments)), sequential(optional(comments), token_identifier, symbol("."), symbol("*"), optional(comments)), sequential(optional(comments), expression, optional(as_column_alias), optional(comments)), sequential(optional(comments), column_alias, symbol("="), expression, optional(comments))), proc_select_one_column)(p)
def as_column_alias(p): return proc(sequential(optional(comments), optional(keyword("AS")), column_alias, optional(comments)), proc_as_column_alias)(p)
def column_alias(p): return proc(parallel(sequential(optional(comments), qualified_item, optional(comments)), sequential(optional(comments), token_string, optional(comments))), proc_column_alias)(p)
def table_view_alias(p): return proc(parallel(sequential(optional(comments), table_name, optional(comments)), sequential(optional(comments), view_name, optional(comments)), sequential(optional(comments), table_alias, optional(comments))), proc_table_view_alias)(p)
def table_name(p): return proc(sequential(optional(comments), qualified_name, optional(comments)), proc_table_name)(p)
def view_name(p): return proc(sequential(optional(comments), qualified_name, optional(comments)), proc_view_name)(p)
def table_alias(p): return proc(sequential(optional(comments), qualified_name, optional(comments)), proc_table_alias)(p)
def from_clause(p): return proc(sequential(optional(comments), keyword("FROM"), table_source_list, optional(comments)), proc_from_clause)(p)
def table_source_list(p): return proc(sequential(optional(comments), table_source, star(next_table_source), optional(comments)), proc_table_source_list)(p)
def next_table_source(p): return proc(sequential(optional(comments), symbol(","), table_source, optional(comments)), proc_next_table_source)(p)
def table_source(p): return proc(sequential(optional(comments), one_table_source, optional(connected_tables), optional(comments)), proc_table_source)(p)
def connected_tables(p): return proc(sequential(optional(comments), more(connected_table), optional(comments)), proc_connected_tables)(p)
def one_table_source(p): return proc(sequential(optional(comments), one_table_item, optional(as_table_alias), optional(paren_list_2), optional(table_hint), optional(pivot_table), optional(comments)), proc_one_table_source)(p)
def one_table_item(p): return proc(parallel(sequential(optional(comments), qualified_item, optional(comments)), sequential(optional(comments), query_expression_group, optional(comments))), proc_one_table_item)(p)
def as_table_alias(p): return proc(sequential(optional(comments), optional(keyword("AS")), table_alias, optional(comments)), proc_as_table_alias)(p)
def pivot_table(p): return proc(sequential(optional(comments), pivot_word, symbol("("), agg_function, keyword("FOR"), in_form, symbol(")"), optional(as_table_alias), optional(comments)), proc_pivot_table)(p)
def pivot_word(p): return proc(parallel(sequential(optional(comments), keyword("PIVOT"), optional(comments)), sequential(optional(comments), keyword("UNPIVOT"), optional(comments))), proc_pivot_word)(p)
def agg_function(p): return proc(sequential(optional(comments), qualified_item, optional(comments)), proc_agg_function)(p)
def table_hint(p): return proc(sequential(optional(comments), keyword("WITH"), paren_list_1, optional(comments)), proc_table_hint)(p)
def connected_table(p): return proc(parallel(sequential(optional(comments), joined_table, optional(comments)), sequential(optional(comments), applied_table, optional(comments))), proc_connected_table)(p)
def joined_table(p): return proc(sequential(optional(comments), join_type, one_table_source, keyword("ON"), search_condition, optional(comments)), proc_joined_table)(p)
def join_type(p): return proc(sequential(optional(comments), optional(join_type_option), optional(keyword("OUTER")), keyword("JOIN"), optional(comments)), proc_join_type)(p)
def join_type_option(p): return proc(parallel(sequential(optional(comments), keyword("INNER"), optional(comments)), sequential(optional(comments), keyword("LEFT"), optional(comments)), sequential(optional(comments), keyword("RIGHT"), optional(comments)), sequential(optional(comments), keyword("FULL"), optional(comments))), proc_join_type_option)(p)
def applied_table(p): return proc(sequential(optional(comments), cross_or_outer, keyword("APPLY"), one_table_source, optional(comments)), proc_applied_table)(p)
def cross_or_outer(p): return proc(parallel(sequential(optional(comments), keyword("CROSS"), optional(comments)), sequential(optional(comments), keyword("OUTER"), optional(comments))), proc_cross_or_outer)(p)
def search_condition(p): return proc(sequential(optional(comments), boolean_item, optional(indent_boolean_items), optional(comments)), proc_search_condition)(p)
def indent_boolean_items(p): return proc(sequential(optional(comments), more(next_boolean_item), optional(comments)), proc_indent_boolean_items)(p)
def group_by(p): return proc(parallel(sequential(optional(comments), group_by_columns, optional(comments)), sequential(optional(comments), group_by_grouping_sets, optional(comments))), proc_group_by)(p)
def group_by_columns(p): return proc(sequential(optional(comments), group_by_word, expression, star(next_expression), optional(comments)), proc_group_by_columns)(p)
def group_by_grouping_sets(p): return proc(sequential(optional(comments), keyword("GROUP"), keyword("BY"), keyword("GROUPING"), keyword("SETS"), symbol("("), symbol("("), expression, star(next_expression), symbol(")"), symbol(")"), optional(comments)), proc_group_by_grouping_sets)(p)
def group_by_word(p): return proc(sequential(optional(comments), keyword("GROUP"), keyword("BY"), optional(comments)), proc_group_by_word)(p)
def order_by_clause(p): return proc(sequential(optional(comments), keyword("ORDER"), keyword("BY"), order_by_one, star(order_by_next), optional(comments)), proc_order_by_clause)(p)
def order_by_next(p): return proc(sequential(optional(comments), symbol(","), order_by_one, optional(comments)), proc_order_by_next)(p)
def order_by_one(p): return proc(sequential(optional(comments), expression, optional(order_by_dir), optional(comments)), proc_order_by_one)(p)
def order_by_dir(p): return proc(parallel(sequential(optional(comments), keyword("ASC"), optional(comments)), sequential(optional(comments), keyword("DESC"), optional(comments))), proc_order_by_dir)(p)
def over_clause(p): return proc(sequential(optional(comments), keyword("OVER"), symbol("("), optional(partition_by_clause), optional(order_by_clause), optional(range_form), symbol(")"), optional(comments)), proc_over_clause)(p)
def partition_by_clause(p): return proc(sequential(optional(comments), keyword("PARTITION"), keyword("BY"), expression, star(next_expression), optional(comments)), proc_partition_by_clause)(p)
def range_form(p): return proc(sequential(optional(comments), row_or_range, keyword("BETWEEN"), range_from_to, keyword("AND"), range_from_to, optional(comments)), proc_range_form)(p)
def row_or_range(p): return proc(parallel(sequential(optional(comments), keyword("ROWS"), optional(comments)), sequential(optional(comments), keyword("RANGE"), optional(comments))), proc_row_or_range)(p)
def range_from_to(p): return proc(parallel(sequential(optional(comments), keyword("CURRENT"), keyword("ROW"), optional(comments)), sequential(optional(comments), range_length, range_dir, optional(comments))), proc_range_from_to)(p)
def range_length(p): return proc(parallel(sequential(optional(comments), keyword("UNBOUNDED"), optional(comments)), sequential(optional(comments), token_number, optional(comments))), proc_range_length)(p)
def range_dir(p): return proc(parallel(sequential(optional(comments), keyword("FOLLOWING"), optional(comments)), sequential(optional(comments), keyword("PRECEDING"), optional(comments))), proc_range_dir)(p)
def expression(p): return proc(sequential(optional(comments), expression_item_1, star(next_expression_item), optional(comments)), proc_expression)(p)
def next_expression_item(p): return proc(sequential(optional(comments), binary_op, expression_item_1, optional(comments)), proc_next_expression_item)(p)
def expression_item_1(p): return proc(sequential(optional(comments), optional(unary_op), expression_item, optional(over_clause), optional(comments)), proc_expression_item_1)(p)
def expression_item(p): return proc(parallel(sequential(optional(comments), cast_form, optional(comments)), sequential(optional(comments), case_form, optional(comments)), sequential(optional(comments), case_form_2, optional(comments)), sequential(optional(comments), iif_form, optional(comments)), sequential(optional(comments), unicode_string, optional(comments)), sequential(optional(comments), count_form, optional(comments)), sequential(optional(comments), qualified_item, optional(comments)), sequential(optional(comments), query_expression_group, optional(comments)), sequential(optional(comments), expression_group, optional(comments)), sequential(optional(comments), number, optional(comments)), sequential(optional(comments), token_string, optional(comments)), sequential(optional(comments), SSIS_parameter, optional(comments)), sequential(optional(comments), sql_variable, optional(comments))), proc_expression_item)(p)
def unicode_string(p): return proc(sequential(optional(comments), keyword("N"), token_string, optional(comments)), proc_unicode_string)(p)
def iif_form(p): return proc(sequential(optional(comments), keyword("IIF"), symbol("("), boolean_expression, symbol(","), expression, symbol(","), expression, symbol(")"), optional(comments)), proc_iif_form)(p)
def count_form(p): return proc(sequential(optional(comments), keyword("COUNT"), symbol("("), optional(keyword("DISTINCT")), count_column, symbol(")"), optional(comments)), proc_count_form)(p)
def count_column(p): return proc(parallel(sequential(optional(comments), symbol("*"), optional(comments)), sequential(optional(comments), expression, optional(comments))), proc_count_column)(p)
def expression_group(p): return proc(sequential(optional(comments), symbol("("), expression, symbol(")"), optional(comments)), proc_expression_group)(p)
def SSIS_parameter(p): return proc(sequential(optional(comments), symbol("?"), optional(comments)), proc_SSIS_parameter)(p)
def sql_variable(p): return proc(sequential(optional(comments), symbol("@"), qualified_item, optional(comments)), proc_sql_variable)(p)
def unary_op(p): return proc(parallel(sequential(optional(comments), symbol("+"), optional(comments)), sequential(optional(comments), symbol("-"), optional(comments))), proc_unary_op)(p)
def binary_op(p): return proc(parallel(sequential(optional(comments), symbol("+"), optional(comments)), sequential(optional(comments), symbol("-"), optional(comments)), sequential(optional(comments), symbol("*"), optional(comments)), sequential(optional(comments), symbol("/"), optional(comments)), sequential(optional(comments), symbol("%"), optional(comments))), proc_binary_op)(p)
def number(p): return proc(parallel(sequential(optional(comments), token_number, optional(decimal_part), optional(comments)), sequential(optional(comments), symbol("."), token_number, optional(comments))), proc_number)(p)
def decimal_part(p): return proc(sequential(optional(comments), symbol("."), optional(token_number), optional(comments)), proc_decimal_part)(p)
def cast_form(p): return proc(sequential(optional(comments), keyword("CAST"), symbol("("), expression, keyword("AS"), qualified_item, symbol(")"), optional(comments)), proc_cast_form)(p)
def case_form(p): return proc(sequential(optional(comments), keyword("CASE"), case_indent, optional(comments)), proc_case_form)(p)
def case_indent(p): return proc(sequential(optional(comments), more(case_when_form), optional(case_else_form), keyword("END"), optional(comments)), proc_case_indent)(p)
def case_when_form(p): return proc(sequential(optional(comments), keyword("WHEN"), boolean_expression, keyword("THEN"), expression, optional(comments)), proc_case_when_form)(p)
def case_else_form(p): return proc(sequential(optional(comments), keyword("ELSE"), expression, optional(comments)), proc_case_else_form)(p)
def case_form_2(p): return proc(sequential(optional(comments), case_expression_2, case_indent_2, optional(comments)), proc_case_form_2)(p)
def case_expression_2(p): return proc(sequential(optional(comments), keyword("CASE"), expression, optional(comments)), proc_case_expression_2)(p)
def case_indent_2(p): return proc(sequential(optional(comments), more(case_when_form_2), optional(case_else_form), keyword("END"), optional(comments)), proc_case_indent_2)(p)
def case_when_form_2(p): return proc(sequential(optional(comments), keyword("WHEN"), expression, keyword("THEN"), expression, optional(comments)), proc_case_when_form_2)(p)
def boolean_expression(p): return proc(sequential(optional(comments), boolean_item, optional(more_boolean_items), optional(comments)), proc_boolean_expression)(p)
def more_boolean_items(p): return proc(sequential(optional(comments), more(next_boolean_item), optional(comments)), proc_more_boolean_items)(p)
def next_boolean_item(p): return proc(sequential(optional(comments), binary_boolean_op, boolean_item, optional(comments)), proc_next_boolean_item)(p)
def binary_boolean_op(p): return proc(parallel(sequential(optional(comments), keyword("AND"), optional(comments)), sequential(optional(comments), keyword("OR"), optional(comments))), proc_binary_boolean_op)(p)
def boolean_item(p): return proc(sequential(optional(comments), star(keyword("NOT")), boolean_one, optional(comments)), proc_boolean_item)(p)
def boolean_one(p): return proc(parallel(sequential(optional(comments), boolean_group, optional(comments)), sequential(optional(comments), expression_compare, optional(comments)), sequential(optional(comments), like_form, optional(comments)), sequential(optional(comments), in_form, optional(comments)), sequential(optional(comments), is_null_form, optional(comments)), sequential(optional(comments), between_form, optional(comments)), sequential(optional(comments), exist_form, optional(comments))), proc_boolean_one)(p)
def boolean_group(p): return proc(sequential(optional(comments), symbol("("), boolean_expression, symbol(")"), optional(comments)), proc_boolean_group)(p)
def expression_compare(p): return proc(sequential(optional(comments), expression, comparison_op, expression, optional(comments)), proc_expression_compare)(p)
def comparison_op(p): return proc(parallel(sequential(optional(comments), symbol(">"), symbol("="), optional(comments)), sequential(optional(comments), symbol(">"), optional(comments)), sequential(optional(comments), symbol("<"), symbol("="), optional(comments)), sequential(optional(comments), symbol("="), optional(comments)), sequential(optional(comments), symbol("<"), symbol(">"), optional(comments)), sequential(optional(comments), symbol("<"), optional(comments)), sequential(optional(comments), symbol("!"), symbol("="), optional(comments))), proc_comparison_op)(p)
def in_form(p): return proc(sequential(optional(comments), expression, optional(keyword("NOT")), keyword("IN"), in_list_or_select, optional(comments)), proc_in_form)(p)
def in_list_or_select(p): return proc(parallel(sequential(optional(comments), in_list, optional(comments)), sequential(optional(comments), in_select, optional(comments))), proc_in_list_or_select)(p)
def in_list(p): return proc(sequential(optional(comments), symbol("("), expression, star(next_expression), symbol(")"), optional(comments)), proc_in_list)(p)
def like_form(p): return proc(sequential(optional(comments), expression, optional(keyword("NOT")), keyword("LIKE"), expression, optional(comments)), proc_like_form)(p)
def in_select(p): return proc(sequential(optional(comments), query_expression_group, optional(comments)), proc_in_select)(p)
def next_expression(p): return proc(sequential(optional(comments), symbol(","), expression, optional(comments)), proc_next_expression)(p)
def is_null_form(p): return proc(sequential(optional(comments), expression, keyword("IS"), optional(keyword("NOT")), keyword("NULL"), optional(comments)), proc_is_null_form)(p)
def between_form(p): return proc(sequential(optional(comments), expression, optional(keyword("NOT")), keyword("BETWEEN"), expression, keyword("AND"), expression, optional(comments)), proc_between_form)(p)
def exist_form(p): return proc(sequential(optional(comments), optional(keyword("NOT")), keyword("EXISTS"), expression, optional(comments)), proc_exist_form)(p)

def run():
    text = open("sample/sample9.sql").read()
    tokens = lexer(text)
    #tokens = [t for t in tokens if t[0] not in ["space", "block_comment", "line_comment"]]
    tokens = [t for t in tokens if t[0] not in ["space"]]
    parser_data["tokens"] = tokens
    p, d = sql_statements(0)
    print(d[0][1])
    #for x in enumerate(d): print(x)

if __name__ == "__main__":
    run()
