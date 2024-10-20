
# export type PyParseResult = { queries: TSQueryAST[]; events: ParseEvent[] };

# def parseFile(sourceFile, transformConfig) -> PyParseResult
 

# def parseCode(fileContent, fileName='unnamed.py', transformConfig=None) -> PyParseResult
# export const parseCode = (
#   fileContent: string,
#   fileName = 'unnamed.ts',
#   transformConfig?: TransformConfig,
# ) => {
#   const sourceFile = ts.createSourceFile(
#     fileName,
#     fileContent,
#     ts.ScriptTarget.ES2015,
#     true,
#   );
#   return parseFile(sourceFile, transformConfig);
# };
