grammar nyaa; // Replace with the actual name of your language

/*  Fragments used by other rules  */
fragment QUOTES: '"';
fragment Printable:  '\t'..'\r' | ' ' .. '~' | '\\t' | '\\n' | '\\r';
fragment ESCAPE: '\\' ('\\' | '"' | 'n' | 't');
fragment Letter: [a-zA-Z_];
fragment Digit: [0-9];

// Starting variable
program: funcDef* MAIN LPAR RPAR TO (LBRACE statements* RBRACE | statements) funcDef*;

//importStatements:
//                  (importStatement
//                | fromImportStatement) ';';
//importStatement: NOTICE ME ID SENPAI;
//fromImportStatement: PLEASE NOTICE ME (ID ('.' ID)+) SENPAI;

// Statements
statements: statement ';' | condStatements | callableStatements ';' | tryCatchStatement;
retStatement: RET expression?;
tryCatchStatement: TRY LBRACE statements* RBRACE EXCEPT LBRACE statements* RBRACE;

statement:(varDef
            | funcDef
            | PASS
            | BREAK
            | CONTINUE
            | retStatement
            | unaryExpressison);


// Callable Statements
callableStatements : printStatement | inputStatement | nameStatement;
printStatement     : PRINT LPAR ((expression | nameStatement) (',' (expression | nameStatement))*)? RPAR;
inputStatement     : INPUT LPAR STR_CONSTANT? RPAR;
nameStatement: ID LPAR (params*) RPAR;

// Conditional Statements
condStatements: forStatement| whileStatement| ifStatement;
forStatement: FOR ID RANGE LPAR expression (',' expression)* RPAR (LBRACE statements* RBRACE);
whileStatement: WHILE LPAR expression RPAR LBRACE statements* RBRACE;
ifStatement: IF LPAR expression RPAR LBRACE statements* RBRACE (elifStatement | elseStatement)*;
elifStatement: ELIF LPAR expression RPAR LBRACE statements* RBRACE;
elseStatement: ELSE LBRACE statements RBRACE;

// Definition Statements
varDef: ID ASSIGN (expression | callableStatements);
funcDef: DEFINE ID LPAR argsList? RPAR TO LBRACE statements* RBRACE;

// Args/Params/Types
type: INT| STR | FLOAT | BOOL;
params : expression (',' expression)*;
argsList: type? ID (',' type? ID)*;

// Expressions
expression         : term (binaryOperator term)*;
unaryExpressison: (NOT | NEG) ID | ID ('++' | '--') | LPAR expression RPAR;
term               : ID
                   | INT_CONSTANT
                   | INT_CONSTANT '.' INT_CONSTANT
                   | STR_CONSTANT
                   | TRUE
                   | FALSE
                   | LPAR expression RPAR
                   | unaryExpressison;
binaryOperator: PLUS| MINUS| MULTIPLY| DIVIDE
                | EQ| NEQ| LT| GT
                | LTE| GTE| AND| OR;

// Lexer rules
PLEASE: 'please';
NOTICE: 'notice';
ME: 'me';
SENPAI: 'senpai';

MAIN : 'nyaa_main';
PRINT : 'printu';
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
TRY: 'ganbatte';
EXCEPT: 'gomenasai';
TRUE: 'HAI';
FALSE: 'IIE';
INT : 'inteja';
STR : 'soturingu';
FLOAT : 'furoto';
BOOL : 'buru';
RET : 'sayonara';
ASSIGN : 'asain';
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

// Skip whitespaces and comments
WS: [ \t\n\r]+ -> skip;
COMMENT: '#' ~[\r\n]* -> skip;

