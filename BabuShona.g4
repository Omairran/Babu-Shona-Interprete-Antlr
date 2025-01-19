grammar BabuShona;

// Entry point
script      : 'Babu' statement* 'Shona';

// Statements
statement   : printStmt 
            | inputStmt 
            | varDecl 
            | ifStmt
            | forLoopStmt
            ;

// If-else statement
ifStmt      
    : 'agar babu' '(' expr ')' block (elseIfStmt)* elseStmt?
    ;

// Else-if statement
elseIfStmt  
    : 'lekin babu' '(' expr ')' block
    ;

// Else statement
elseStmt    
    : 'magar shona' block
    ;

// Print statement
printStmt
    : 'dekho babu' expr
    ;

// Input statement
inputStmt   
    : 'bolo shona' IDENTIFIER
    ;

// Variable declaration
varDecl     
    : 'mela babu' IDENTIFIER '=' expr
    ;

// For loop statement
forLoopStmt 
    : 'chalo babu' IDENTIFIER '=' expr 'se lekar' expr ('tak' expr)? 'uchal ke' expr block
    ;

// Block of statements
block       
    : '{' statement* '}'
    ;

// Expressions
expr        
    : expr ('+' | '-' | '*' | '/') expr         # arithmeticExpr
    | expr ('<' | '<=' | '>' | '>=' | '==' | '!=') expr # comparisonExpr
    | expr ('and' | 'or') expr                 # logicalExpr
    | 'not' expr                              # notExpr
    | '(' expr ')'                            # parenthesesExpr
    | BOOL                                    # booleanExpr
    | IDENTIFIER                              # variableExpr
    | INT                                     # intExpr
    | STRING                                  # stringExpr
    ;

// Lexer rules
BOOL        : 'True' | 'False';                // Boolean values
IDENTIFIER  : [a-zA-Z_][a-zA-Z0-9_]*;          // Variable names
INT         : [0-9]+;                          // Integer values
STRING      : '"' .*? '"';                     // String values 
WS          : [ \t\r\n]+ -> skip;              // Skip whitespace
