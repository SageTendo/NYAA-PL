grammar nyaa; // Replace with the actual name of your language

/*  Fragments used by other rules  */
fragment QUOTES: '"';
fragment Printable:  '\t'..'\r' | ' ' .. '~' | '\\t' | '\\n' | '\\r';
fragment ESCAPE: '\\' ('\\' | '"' | 'n' | 't');
fragment Letter: [a-zA-Z_];
fragment Digit: [0-9];

//importStatements:
//                  (importStatement
//                | fromImportStatement) ';';
//importStatement: NOTICE ME ID SENPAI;
//fromImportStatement: PLEASE NOTICE ME (ID ('.' ID)+) SENPAI;

// Starting variable
program            : funcDef* MAIN LPAR RPAR TO (LBRACE body RBRACE | statement ';') | EOF;
funcDef            : DEFINE ID LPAR (ID (',' ID)*)? RPAR TO LBRACE body RBRACE;

// Statements
body               : statement*;
conditionalBody    : statement conditionalBody? | BREAK | CONTINUE;

statement          : PASS
                    |assignmentStatement
                    |retStatement
                    |whileStatement
                    |ifStatement
                    |printStatement
                    |inputStatement
                    |callStatement
                    |postfixExpression;

assignmentStatement: ID ASSIGN (expression | callableStatements);
retStatement       : RET expression?;

// Args
args               : LPAR ((expression|callableStatements) (',' (expression|callableStatements))*)? RPAR;

// Callable Statements
callableStatements : printStatement | inputStatement | callStatement;
printStatement     : PRINT args;
inputStatement     : INPUT LPAR STR_CONSTANT? RPAR;
callStatement      : ID args;

// Conditional Statements
whileStatement     : WHILE LPAR expression RPAR LBRACE (CONTINUE | BREAK | conditionalBody) RBRACE;
ifStatement        : IF LPAR expression RPAR LBRACE conditionalBody RBRACE elifStatement* elseStatement?;
elifStatement      : ELIF LPAR expression RPAR LBRACE conditionalBody RBRACE;
elseStatement      : ELSE LBRACE conditionalBody RBRACE;

// Expressions
postfixExpression  : ID (UN_ADD | UN_SUB);
expression         : simple | simple relOperator expression;
simple             : term | term addOp simple;
term               : factor | factor mulOp term;
factor             : NEG arithFactor
                    |NOT boolFactor
                    |LPAR expression RPAR
                    |ID
                    |TRUE
                    |FALSE
                    |INT_CONSTANT
                    |FLOAT_CONSTANT
                    |STR_CONSTANT;
arithFactor         : NEG arithFactor | ID | INT_CONSTANT | FLOAT_CONSTANT;
boolFactor          : NOT boolFactor  | ID | INT_CONSTANT | FLOAT_CONSTANT | STR_CONSTANT | TRUE | FALSE;


addOp              : PLUS | MINUS | OR;
mulOp              : AND | DIVIDE | MULTIPLY;
relOperator       : EQ| NEQ| LT| GT
                    | LTE| GTE;

// Lexer rules
PLEASE: 'please';
NOTICE: 'notice';
ME: 'me';
SENPAI: 'senpai';

MAIN : 'uWu_nyaa';
PRINT : 'yomu';
INPUT : 'ohayo';
WHILE : 'daijoubu';
FOR : 'uWu';
IF : 'nani';
ELIF : 'nandesuka';
ELSE : 'baka';
RANGE: 'from';
BREAK: 'yamete';
CONTINUE: 'motto';
PASS: 'pasu';
DEFINE: 'kawaii';
TRUE: 'HAI';
FALSE: 'IIE';
RET : 'modoru';
ASSIGN : 'wa';
PLUS : 'purasu';
MINUS : 'mainasu';
MULTIPLY : 'purodakuto';
DIVIDE : 'supuritto';
AND : 'ando';
OR : 'matawa';
NOT : 'nai';

TO: '=>';
LPAR : '(' ;
RPAR : ')';
LBRACE : '{';
RBRACE : '}';
SEMICOLON : ';';
EQ : '==';
NEQ : '!=';
LT : '<';
GT : '>';
LTE : '<=';
GTE : '>=';
UN_ADD : '++' ;
UN_SUB : '--' ;
NEG : '-';
PERIOD : '.';

//RBRACKET : ']';
//LBRACKET : '[';
//COLON : ':';
//TYPE_ASSIGN : '::';
//DIV: '//';
//MODULO : '%';

// Type definitions
ID : (Letter | '_') (Letter | Digit | '_')*;
INT_CONSTANT : Digit+;
STR_CONSTANT : '"' ~[\r\n"]* '"';
FLOAT_CONSTANT: INT_CONSTANT '.' INT_CONSTANT;

// Skip whitespaces and comments
WS: [ \t\n\r]+ -> skip;
COMMENT: '#' ~[\r\n]* -> skip;


