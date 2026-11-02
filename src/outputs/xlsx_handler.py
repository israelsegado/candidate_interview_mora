from openpyxl import Workbook 

def write_xlsx(rows, path, columns): 
    wb = Workbook() 
    ws = wb.active 
    ws.title = "Report" 
    ws.append(columns) 

    for row in rows: 
        ws.append([row.get(c, "") for c in columns]) 
    wb.save(path)