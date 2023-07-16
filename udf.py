from udf_base import *

#undefined:
#token_bracketed
#token_identifier
#token_number
#token_quoted
#token_string

proc_select_list = indent
proc_connected_tables = indent
proc_indent_boolean_items = indent
proc_case_indent = indent
proc_case_indent_2 = indent
proc_sp_parameter_list_1 = indent
proc_sp_parameter_list_group = concat_newline
proc_table_source = concat_newline
proc_query_expression_group = concat_newline
proc_query_specification = concat_newline
proc_table_source_list = concat_newline
proc_search_condition = concat_newline
proc_with_cte = concat_double_line
proc_case_form = concat_newline
proc_case_form_2 = concat_newline
proc_create_procedure_sig = concat_newline
proc_create_function_sig = concat_newline
proc_insert_statement = concat_newline
proc_value_clause = concat_newline
proc_create_procedure = concat_double_line
proc_create_function = concat_double_line
proc_merge_statement = concat_double_line
#proc_merge_when = concat_newline
proc_select_statement = concat_double_line
proc_query_statement = concat_double_line
proc_next_query_expression = concat_double_line
proc_sp_def_body = concat_double_line
proc_sql_statements = concat_double_line
proc_begin_end_block = concat_double_line
proc_begin_try_block = concat_double_line
proc_query_expression = concat_double_line
proc_subquery_expression = indent
proc_sql_variable = concat_tight
proc_number = concat_tight
proc_decimal_part = concat_tight
proc_comparison_op = concat_tight
proc_temp_table = concat_tight
proc_unicode_string = concat_tight
proc_name = concat_tight
proc_set_update_list = indent_next
proc_paren_list_2 = indent_next
proc_column_full_spec = indent_next
proc_if_statement = concat_newline
proc_if_statement_else = concat_newline
proc_while_statement = concat_newline


proc_in_list = paren_list(7)
proc_paren_list_3 = paren_list(7)
proc_column_spec = paren_list(7)
proc_group_by_columns = next_list(5)

def proc_comments(d):
    d = [x.strip() for t,x in d]
    x = "\n"+ "\n".join(d) + "\n"
    return [("processed", x)]