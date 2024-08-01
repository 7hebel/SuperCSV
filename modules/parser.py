from modules import datatype
from modules import errors

from dataclasses import dataclass
from io import StringIO
import filelock
import csv


type T_Row = dict[str, datatype.LowType]


@dataclass
class SCSVObject:
    annotations: dict[str, datatype._HighType]
    fields: list[str]
    enc_rows: list[T_Row]
    file_path: str | None = None
    raw_header: str | None = None
    
    def __getitem__(self, index: int) -> T_Row | None:
        return self.read(index)    

    def __setitem__(self, index: int, row_data: T_Row) -> None:
        return self.update_row(index, row_data)
    
    def read_all(self):
        for enc_row in self.enc_rows:
            dec_row = self._decode_row(enc_row)
            yield dec_row
            
    def read(self, index: int) -> T_Row | None:
        """ Returns row at given index or None if index is invalid. """
        try:
            self._validate_index(index)
            return self._decode_row(self.enc_rows[index])

        except IndexError:
            return None
        
    def update_row(self, index: int, row_data: T_Row) -> None:
        """ Override entire row. """
        self._validate_index(index)
        
        encoded_row = self._encode_row(row_data)
        self.enc_rows[index] = encoded_row
        self._save()
        
    def update_field(self, index: int, col: str, value: datatype._HighType) -> None:
        """ Update single column in a row. """
        self._validate_index(index)

        if col not in self.annotations:
            raise errors.UpdateError(f"Invalid column: \"{col}\"")
        
        value = self.annotations.get(col).encode(value)
        self.enc_rows[index][col] = value
        self._save()
        
    def remove_row(self, index: int) -> None:
        """ Remove row by it's index. """
        self._validate_index(index)
        self.enc_rows.pop(index) 
        self._save()   
        
    def insert_row(self, row_data: T_Row) -> None:
        """ Insert new row. """
        encoded_row = self._encode_row(row_data)
        self.enc_rows.append(encoded_row)
        self._save()
        
    def _validate_index(self, index: int) -> None:
        """ Check if given index is correct. Raises IndexError if not. """
        if not isinstance(index, int):
            raise IndexError(f"Invalid index type: {type(index)}.")
        if index not in range(0, len(self.enc_rows)):
            raise IndexError(f"Invalid row index: {index}. Total rows in object = {len(self.enc_rows)}")
        
    def _encode_row(self, data: T_Row) -> T_Row:
        casted = {}
        
        for col, val in data.items():
            if col not in self.annotations:
                raise errors.UpdateError(f"Invalid column: {col}")
            
            casted[col] = self.annotations.get(col).encode(val)
        
        return casted
    
    def _decode_row(self, data: T_Row) -> T_Row:
        decoded = {}
        
        for col, val in data.items():
            if col not in self.annotations:
                raise errors.UpdateError(f"Invalid column: {col}")
            
            decoded[col] = self.annotations.get(col).decode(val)
            
        return decoded
    
    def _save(self):
        if not self.file_path:
            return
        
        lock_fp = self.file_path + ".lock"
        with filelock.FileLock(lock_fp):
            with open(self.file_path, "w") as file:
                content = self.raw_header + "@@\n"
                content += ",".join(self.fields) + "\n"
                content += "\n".join(",".join(map(str, row.values())) for row in self.enc_rows) + "\n"
                file.write(content)           
                
        
def _parse(raw_content: str, fp: str | None = None) -> SCSVObject:   
    if "@@" not in raw_content:
        raise errors.ParseError("Header separator not found \"@@\"")
    
    header, raw_data = raw_content.split("@@")
    
    annotations = _parse_header(header.strip())
    raw_data = StringIO(raw_data.strip())
    
    reader = csv.DictReader(raw_data)
    fields = reader.fieldnames
        
    _ensure_types_coverage(fields, annotations)
        
    rows = _dictreader_to_rows(reader)
        
    return SCSVObject(
        annotations=annotations,
        fields=fields,
        enc_rows=rows,
        file_path=fp,
        raw_header=header
    )


def _parse_header(header: str) -> dict[str, datatype._HighType]:
    """ Parse file annotations with syntax: "COLUMN NAME: TYPE NAME" """
    annotations = {}
    
    for annotation in header.split("\n"):
        if not annotation:
            continue
        
        column, type_name = annotation.split(":")
        column = column.strip()
        type_name = type_name.lower().strip()

        if type_name not in datatype.ANNOTATIONS_TABLE:
            raise errors.ParseError(f"Invalid data type found for: {column} (\"{type_name}\")")
        
        annotations[column] = datatype.ANNOTATIONS_TABLE.get(type_name)
        
    return annotations
       
       
def _ensure_types_coverage(fields: list[str], annotations: dict[str, datatype._HighType]) -> None:
    """ Check if all fields has been correctly typed. Raises AnnotationCoverageError."""
    for field in fields:
        if field not in annotations:
            raise errors.AnnotationCoverageError(f"Not annotated field: \"{field}\"")
        
    for annotated_field in annotations.keys():
        if annotated_field not in fields:
            raise errors.AnnotationCoverageError(f"Annotated invalid field: \"{annotated_field}\"")
        
    return None
        

def _dictreader_to_rows(reader: csv.DictReader) -> list[dict[str, datatype.LowType]]:
    return [row for row in reader] 
        