create_procedure ::= 
CREATE . (
    PROCEDURE | PROC) . qualified_name . (
    sp_parameter_list | NOTHING) . AS . sql_statements;

create_function ::= 
CREATE . (
    FUNCTION | FUNC) . qualified_name . (
    sp_parameter_list | NOTHING) . (
    (
    RETURNS . qualified_item) | NOTHING) . (
    AS | NOTHING) . sql_statements;

sql_statements ::= 
repeat(sql_statement);

qualified_name ::= 
(
    scope_qualified | NOTHING) . name;

sp_parameter_list ::= 
sp_parameter_list_1 | '(' . sp_parameter_list_1 . ')';

qualified_item ::= 
(
    scope_qualified | NOTHING) . name_or_function;

sql_statement ::= 
(
    (
        (
        WITH . cte . (
            repeat((
            ',' . cte)) | NOTHING)) | NOTHING) . (
        INSERT . (
            INTO | NOTHING) . qualified_name . (
            paren_list_3 | NOTHING) . (
            value_clause | query_expression . (
                order_by_clause | NOTHING)) | UPDATE . table_name . (
            as_table_alias | NOTHING) . SET . update_one . (
            repeat(update_next) | NOTHING) . (
            from_clause | NOTHING) . (
            where_clause | NOTHING) . (
            group_by | NOTHING) . (
            having_clause | NOTHING) | DELETE . (
            from_clause | NOTHING) . (
            where_clause | NOTHING) . (
            group_by | NOTHING) . (
            having_clause | NOTHING) | query_expression | MERGE . table_name . (
            as_table_alias | NOTHING) . USING . one_table_source . (
            as_table_alias | NOTHING) . ON . boolean_expression . repeat((
            WHEN . (
                NOT | NOTHING) . MATCHED . (
                (
                BY . SOURCE | BY . TARGET) | NOTHING) . (
                (
                AND . boolean_expression) | NOTHING) . THEN . (
                INSERT . paren_list_3 . VALUES . paren_list_2 | UPDATE . SET . update_one . (
                    repeat(update_next) | NOTHING))))) | (
        DECLARE . sql_variable . TABLE . '(' . declare_table_column . (
            repeat((
            ',' . declare_table_column)) | NOTHING) . ')' | DECLARE . declare_one_var . (
            repeat((
            ',' . declare_one_var)) | NOTHING)) | RETURN . (
        expression | NOTHING) | WHILE . boolean_expression . sql_statement | BREAK | CONTINUE | SET . set_one_var . (
        repeat((
        ',' . set_one_var)) | NOTHING) | CREATE . TABLE . table_or_view_name . '(' . one_column_full_spec . (
        repeat((
        ',' . one_column_full_spec)) | NOTHING) . ')' | CREATE . (
        (
        CLUSTERED | NONCLUSTERED) | NOTHING) . INDEX . qualified_name . ON . qualified_name . paren_list_1 | SET . (
        COUNT | NOCOUNT | IDENTITY_INSERT . (
            qualified_item | NOTHING)) . (
        ON | OFF) | BEGIN . TRY . repeat(sql_statement) . END . TRY . BEGIN . CATCH . repeat(sql_statement) . END . CATCH | BEGIN . repeat(sql_statement) . END | IF . boolean_expression . sql_statement . (
        (
        ELSE . sql_statement) | NOTHING) | (
        EXEC | EXECUTE) . expression . (
        (
        exec_one_para . (
            repeat((
            ',' . exec_one_para)) | NOTHING)) | NOTHING) | DROP . (
        TABLE . table_or_view_name | VIEW . table_or_view_name) | (
        TRUNCATE | TRUNC) . TABLE . qualified_item | RAISERROR . function_parameters) . (
    ';' | NOTHING) | ';';

scope_qualified ::= 
name_or_function . qualifier . (
    repeat((
    (
        name_or_function | NOTHING) . qualifier)) | NOTHING);

name ::= 
bare_name | '@' . bare_name | '#' . bare_name;

sp_parameter_list_1 ::= 
sp_parameter . (
    repeat((
    ',' . sp_parameter)) | NOTHING);

name_or_function ::= 
name . (
    function_parameters | NOTHING);

cte ::= 
name . (
    paren_list_3 | NOTHING) . AS . query_expression_group;

paren_list_3 ::= 
'(' . expression . (
    repeat(next_expression) | NOTHING) . ')';

value_clause ::= 
VALUES . value_one . (
    repeat((
    ',' . value_one)) | NOTHING);

query_expression ::= 
query_expression_one . (
    repeat((
    (
        UNION . (
            ALL | NOTHING) | EXCEPT | INTERSECT) . query_expression_one)) | NOTHING);

order_by_clause ::= 
ORDER . BY . order_by_one . (
    repeat((
    ',' . order_by_one)) | NOTHING);

table_name ::= 
qualified_name;

as_table_alias ::= 
(
    AS | NOTHING) . table_alias;

update_one ::= 
qualified_item . '=' . expression;

update_next ::= 
',' . update_one;

from_clause ::= 
FROM . table_source . (
    repeat((
    ',' . table_source)) | NOTHING);

where_clause ::= 
WHERE . search_condition;

group_by ::= 
GROUP . BY . expression . (
    repeat(next_expression) | NOTHING) | GROUP . BY . GROUPING . SETS . '(' . '(' . expression . (
    repeat(next_expression) | NOTHING) . ')' . ')';

having_clause ::= 
HAVING . search_condition;

one_table_source ::= 
(
    qualified_item | query_expression_group) . (
    as_table_alias | NOTHING) . (
    paren_list_2 | NOTHING) . (
    (
    WITH . paren_list_1) | NOTHING) . (
    (
    (
        PIVOT | UNPIVOT) . '(' . qualified_item . FOR . in_form . ')' . (
        as_table_alias | NOTHING)) | NOTHING);

boolean_expression ::= 
boolean_item . (
    repeat(next_boolean_item) | NOTHING);

paren_list_2 ::= 
'(' . expression . (
    repeat(next_expression) | NOTHING) . ')';

sql_variable ::= 
'@' . qualified_item;

declare_table_column ::= 
qualified_item . qualified_item . (
    repeat(qualified_item) | NOTHING);

declare_one_var ::= 
sql_variable . data_type . (
    variable_init | NOTHING);

expression ::= 
expression_item_1 . (
    repeat((
    (
        '+' | '-' | '*' | '/' | '%') . expression_item_1)) | NOTHING);

set_one_var ::= 
sql_variable . variable_init;

table_or_view_name ::= 
qualified_name;

one_column_full_spec ::= 
repeat((
    (
        NOT | NOTHING) . NULL | qualified_item));

paren_list_1 ::= 
'(' . expression . (
    repeat(next_expression) | NOTHING) . ')';

exec_one_para ::= 
(
    (
    sql_variable . '=') | NOTHING) . expression;

function_parameters ::= 
'(' . (
    (
    parameter . (
        repeat((
        ',' . parameter)) | NOTHING)) | NOTHING) . ')';

qualifier ::= 
'.';

bare_name ::= 
token_identifier | token_quoted | token_bracketed;

sp_parameter ::= 
sql_variable . data_type . (
    variable_init | NOTHING);

query_expression_group ::= 
'(' . query_expression . ')';

next_expression ::= 
',' . expression;

value_one ::= 
paren_list_1;

query_expression_one ::= 
SELECT . (
    (
    ALL | DISTINCT) | NOTHING) . (
    (
    TOP . expression . (
        PERCENT | NOTHING)) | NOTHING) . select_one_column_1 . (
    repeat((
    ',' . select_one_column_1)) | NOTHING) . (
    (
    INTO . qualified_item) | NOTHING) . (
    from_clause | NOTHING) . (
    where_clause | NOTHING) . (
    group_by | NOTHING) . (
    having_clause | NOTHING) . (
    order_by_clause | NOTHING) . (
    FOR . XML . (
    (
        RAW | AUTO) . (
        xml_element | NOTHING) . (
        xml_option | NOTHING) | PATH . (
        xml_element | NOTHING) . (
        xml_option | NOTHING)) | NOTHING) . (
    (
    OPTION . '(' . option_one . (
        repeat((
        ',' . option_one)) | NOTHING) . ')') | NOTHING) | value_clause | query_expression_group;

order_by_one ::= 
expression . (
    (
    ASC | DESC) | NOTHING);

table_alias ::= 
qualified_name;

table_source ::= 
one_table_source . (
    repeat((
    (
        (
        INNER | LEFT | RIGHT | FULL) | NOTHING) . (
        OUTER | NOTHING) . JOIN . one_table_source . ON . search_condition | (
        CROSS | OUTER) . APPLY . one_table_source)) | NOTHING);

search_condition ::= 
boolean_item . (
    repeat(next_boolean_item) | NOTHING);

in_form ::= 
expression . (
    NOT | NOTHING) . IN . (
    '(' . expression . (
        repeat(next_expression) | NOTHING) . ')' | query_expression_group);

boolean_item ::= 
(
    repeat(NOT) | NOTHING) . (
    '(' . boolean_expression . ')' | expression . (
        '>' . '=' | '>' | '<' . '=' | '=' | '<' . '>' | '<' | '!' . '=') . expression | expression . (
        NOT | NOTHING) . LIKE . expression | in_form | expression . IS . (
        NOT | NOTHING) . NULL | expression . (
        NOT | NOTHING) . BETWEEN . expression . AND . expression | (
        NOT | NOTHING) . EXISTS . expression);

next_boolean_item ::= 
(
    AND | OR) . boolean_item;

data_type ::= 
qualified_item;

variable_init ::= 
'=' . expression;

expression_item_1 ::= 
(
    (
    '+' | '-') | NOTHING) . (
    CAST . '(' . expression . AS . qualified_item . ')' | CASE . repeat((
        WHEN . boolean_expression . THEN . expression)) . (
        case_else_form | NOTHING) . END | CASE . expression . repeat((
        WHEN . expression . THEN . expression)) . (
        case_else_form | NOTHING) . END | IIF . '(' . boolean_expression . ',' . expression . ',' . expression . ')' | N . token_string | COUNT . '(' . (
        DISTINCT | NOTHING) . (
        '*' | expression) . ')' | qualified_item | query_expression_group | '(' . expression . ')' | (
        token_number . (
            (
            '.' . (
                token_number | NOTHING)) | NOTHING) | '.' . token_number) | token_string | '?' | sql_variable) . (
    (
    OVER . '(' . (
        (
        PARTITION . BY . expression . (
            repeat(next_expression) | NOTHING)) | NOTHING) . (
        order_by_clause | NOTHING) . (
        (
        (
            ROWS | RANGE) . BETWEEN . range_from_to . AND . range_from_to) | NOTHING) . ')') | NOTHING);

parameter ::= 
(
    DISTINCT | NOTHING) . expression;

select_one_column_1 ::= 
(
    (
    sql_variable . '=') | NOTHING) . (
    '*' | token_identifier . '.' . '*' | expression . (
        (
        (
            AS | NOTHING) . column_alias) | NOTHING) | column_alias . '=' . expression);

xml_element ::= 
'(' . token_string . ')';

xml_option ::= 
',' . ELEMENTS;

option_one ::= 
repeat(expression);

case_else_form ::= 
ELSE . expression;

range_from_to ::= 
CURRENT . ROW | (
    UNBOUNDED | token_number) . (
    FOLLOWING | PRECEDING);

column_alias ::= 
qualified_item | token_string;

