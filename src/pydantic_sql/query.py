

const debugQuery = debugBase('client:query');


# Startup function
## Params: DB options
# Connect to DB

# Run Query Function
## Params: query string, queue?
## Send the query to the queue.


# IQueryTypes
## Params: paramMetadata, includes the mappings and the params
## Return: IQueryTypes



# export interface IParseError {
#   errorCode: string;
#   hint?: string;
#   message: string;
#   position?: string;
# }

# interface TypeField {
#   name: string;
#   tableOID: number;
#   columnAttrNumber: number;
#   typeOID: number;
#   typeSize: number;
#   typeModifier: number;
#   formatCode: number;
# }

# type TypeData =
#   | {
#       fields: Array<TypeField>;
#       params: Array<{ oid: number }>;
#     }
#   | IParseError;

# /**
#  * Returns the raw query type data as returned by the Describe message
#  * @param query query string, can only contain proper Postgres numeric placeholders
#  * @param query name, should be unique per query body
#  * @param queue
#  */

# getTypeData function
## Params: query string, queue?
## Return: TypeData


# enum TypeCategory {
#   ARRAY = 'A',
#   BOOLEAN = 'B',
#   COMPOSITE = 'C',
#   DATE_TIME = 'D',
#   ENUM = 'E',
#   GEOMETRIC = 'G',
#   NETWORK_ADDRESS = 'I',
#   NUMERIC = 'N',
#   PSEUDO = 'P',
#   STRING = 'S',
#   TIMESPAN = 'T',
#   USERDEFINED = 'U',
#   BITSTRING = 'V',
#   UNKNOWN = 'X',
# }

# interface TypeRow {
#   oid: string;
#   typeName: string;
#   typeKind: string;
#   enumLabel: string;
#   typeCategory?: TypeCategory;
#   elementTypeOid?: string;
# }

# // Aggregate rows from database types catalog into MappableTypes
# export function reduceTypeRows(
#   typeRows: TypeRow[],
# ): Record<string, MappableType> {
#   const enumTypes = typeRows
#     .filter((r) => r.typeKind === DatabaseTypeKind.Enum)
#     .reduce((typeMap, { oid, typeName, enumLabel }) => {
#       const typ = typeMap[oid] ?? typeName;

#       // We should get one row per enum value
#       return {
#         ...typeMap,
#         [oid]: {
#           name: typeName,
#           // Merge enum values
#           enumValues: [...(isEnum(typ) ? typ.enumValues : []), enumLabel],
#         },
#       };
#     }, {} as Record<string, MappableType>);
#   return typeRows.reduce(
#     (typeMap, { oid, typeName, typeCategory, elementTypeOid }) => {
#       // Attempt to merge any partially defined types
#       const typ = typeMap[oid] ?? typeName;

#       if (oid in enumTypes) {
#         return { ...typeMap, [oid]: enumTypes[oid] };
#       }

#       if (
#         typeCategory === TypeCategory.ARRAY &&
#         elementTypeOid &&
#         elementTypeOid in enumTypes
#       ) {
#         return {
#           ...typeMap,
#           [oid]: {
#             name: typeName,
#             elementType: enumTypes[elementTypeOid],
#           },
#         };
#       }

#       return { ...typeMap, [oid]: typ };
#     },
#     {} as Record<string, MappableType>,
#   );
# }

# // TODO: self-host
# async function runTypesCatalogQuery(
#   typeOIDs: number[],
#   queue: AsyncQueue,
# ): Promise<TypeRow[]> {
#   let rows: any[];
#   if (typeOIDs.length > 0) {
#     const concatenatedTypeOids = typeOIDs.join(',');
#     rows = await runQuery(
#       `
# SELECT pt.oid, pt.typname, pt.typtype, pe.enumlabel, pt.typelem, pt.typcategory
# FROM pg_type pt
# LEFT JOIN pg_enum pe ON pt.oid = pe.enumtypid
# WHERE pt.oid IN (${concatenatedTypeOids})
# OR pt.oid IN (SELECT typelem FROM pg_type ptn WHERE ptn.oid IN (${concatenatedTypeOids}));
# `,
#       queue,
#     );
#   } else {
#     rows = [];
#   }
#   return rows.map(
#     ([oid, typeName, typeKind, enumLabel, elementTypeOid, typeCategory]) => ({
#       oid,
#       typeName,
#       typeKind,
#       enumLabel,
#       elementTypeOid,
#       typeCategory,
#     }),
#   );
# }

interface ColumnComment {
  tableOID: number;
  columnAttrNumber: number;
  comment: string;
}

async function getComments(
  fields: TypeField[],
  queue: AsyncQueue,
): Promise<ColumnComment[]> {
  const columnFields = fields.filter((f) => f.columnAttrNumber > 0);
  if (columnFields.length === 0) {
    return [];
  }

  const matchers = columnFields.map(
    (f) => `(objoid=${f.tableOID} and objsubid=${f.columnAttrNumber})`,
  );
  const selection = matchers.join(' or ');

  const descriptionRows = await runQuery(
    `SELECT
      objoid, objsubid, description
     FROM pg_description WHERE ${selection};`,
    queue,
  );

  return descriptionRows.map((row) => ({
    tableOID: Number(row[0]),
    columnAttrNumber: Number(row[1]),
    comment: row[2],
  }));
}

export async function getTypes(
  queryData: InterpolatedQuery,
  queue: AsyncQueue,
): Promise<IQueryTypes | IParseError> {
  const typeData = await getTypeData(queryData.query, queue);
  if ('errorCode' in typeData) {
    return typeData;
  }

  const { params, fields } = typeData;

  const paramTypeOIDs = params.map((p) => p.oid);
  const returnTypesOIDs = fields.map((f) => f.typeOID);
  const usedTypesOIDs = paramTypeOIDs.concat(returnTypesOIDs);
  const typeRows = await runTypesCatalogQuery(usedTypesOIDs, queue);
  const commentRows = await getComments(fields, queue);
  const typeMap = reduceTypeRows(typeRows);

  const attrMatcher = ({
    tableOID,
    columnAttrNumber,
  }: {
    tableOID: number;
    columnAttrNumber: number;
  }) => `(attrelid = ${tableOID} and attnum = ${columnAttrNumber})`;

  const attrSelection =
    fields.length > 0 ? fields.map(attrMatcher).join(' or ') : false;

  const attributeRows = await runQuery(
    `SELECT
      (attrelid || ':' || attnum) AS attid, attname, attnotnull
     FROM pg_attribute WHERE ${attrSelection};`,
    queue,
  );
  const attrMap: {
    [attid: string]: {
      columnName: string;
      nullable: boolean;
    };
  } = attributeRows.reduce(
    (acc, [attid, attname, attnotnull]) => ({
      ...acc,
      [attid]: {
        columnName: attname,
        nullable: attnotnull !== 't',
      },
    }),
    {},
  );

  const getAttid = (col: Pick<TypeField, 'tableOID' | 'columnAttrNumber'>) =>
    `${col.tableOID}:${col.columnAttrNumber}`;

  const commentMap: { [attid: string]: string | undefined } = {};
  for (const c of commentRows) {
    commentMap[`${c.tableOID}:${c.columnAttrNumber}`] = c.comment;
  }

  const returnTypes = fields.map((f) => ({
    ...attrMap[getAttid(f)],
    ...(commentMap[getAttid(f)] ? { comment: commentMap[getAttid(f)] } : {}),
    returnName: f.name,
    type: typeMap[f.typeOID],
  }));

  const paramMetadata = {
    params: params.map(({ oid }) => typeMap[oid]),
    mapping: queryData.mapping,
  };

  return { paramMetadata, returnTypes };
}