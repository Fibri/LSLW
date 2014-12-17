import re

def parseCells(str):
    data = []
    
    cells = str.split('I,')
    for i in range(len(cells)-1):
        cells[i] = cells[i]+"I"
    
    """
    <#cells>CELLS:<cellid>(<x>,<y>)'<radius>'<offsize>'<defsize>'<prod>,...;\
    """
    p = re.compile("(\d+)\((.*),(.*)\)'(\d+)'(\d+)'(\d+)'(\I*)")
    
    for cell in cells:
        res = re.search(p, cell)
        groups = res.groups()
        
        """
        groups :
        0 : id
        1 : x
        2 : y
        3 : radius
        4 : offsize
        5 : defsize
        7 : prod
        """
        
        cellData = {
        'id':int(groups[0]),
        'x':int(groups[1]),
        'y':int(groups[2]),
        'radius':int(groups[3]),
        'offsize':int(groups[4]),
        'defsize':int(groups[5]),
        'prod':len(groups[6])
        }
        
        data.append(cellData)
    
    return data
    
def parseLines(str):
    data = []
    
    lines = str.split(',')
    
    """
    <#lines>LINES:<cellid>@<dist>OF<cellid>,...
    """
    p = re.compile("(\d+)@(\d+)OF(\d+)")
    
    for line in lines:
        res = re.search(p, line)
        groups = res.groups()
        
        """
        groups :
        0 : id
        1 : dist
        2 : target
        """
        
        lineData = {
        'id':int(groups[0]),
        'dist':int(groups[1]),
        'target':int(groups[2])
        }
        
        data.append(lineData)
    
    return data
    
def parseCellsState(str):
    data = []
    
    cells = str.split(',')
    
    """
    <cellid>[<owner>]<offunits>'<defunits>,...;\
    """
    p = re.compile("(\d+)\[(\d+)\](\d+)'(\d+)")
    
    for cell in cells:
        res = re.search(p, cell)
        groups = res.groups()
        
        """
        groups :
        0 : id
        1 : owner
        2 : offunits
        3 : defunits
        """
        
        cellData = {
        'id':int(groups[0]),
        'owner':int(groups[1]),
        'offunits':int(groups[2]),
        'defunits':int(groups[3])
        }
        
        data.append(cellData)
    
    return data

def parseMovesState(str):
    data = []
    
    moves = str.split(',')
    
    """
    <#moves>MOVES:<cellid><direction><#units>[<owner>]@<timestamp>'...<cellid>
    """
    
    p = re.compile("(.*)'(\d+)$")
    p2 = re.compile("(\d*)([<>])(\d+)\[(\d+)\]@(\d+)")
    
    for move in moves:
        res = re.search(p, move)
        groups = res.groups()
        
        movesInLine = groups[0].split("'")
        currentLine = int(groups[1])
        
        for mov in movesInLine:
            res2 = re.search(p2, mov)
            groups = res2.groups()
            
            """
            groups :
            0 : targetId
            1 : direction
            2 : unitNb
            3 : owner
            4 : timestamp
            """
            if(groups[1] == '<'):
                movData = {
                    'targetId':int(groups[0]),
                    'unitNb':int(groups[2]),
                    'owner':int(groups[3]),
                    'timestamp':int(groups[4]),
                    'sourceId':currentLine
                }
            else:
                movData = {
                    'targetId':currentLine,
                    'unitNb':int(groups[2]),
                    'owner':int(groups[3]),
                    'timestamp':int(groups[4]),
                    'sourceId':None
                }
            data.append(movData)
    
    return data

def analyzeState(str):
    """
    STATE<matchid>IS<#players>;
    <#cells>CELLS:<cellid>[<owner>]<offunits>'<defunits>,...;\
    <#moves>MOVES:<cellid><direction><#units>[<owner>]@<timestamp>'...<cellid>,...
    """
    p = re.compile("STATE(.*)IS(\d+);(\d+)CELLS:(.*);(\d+)MOVES:(.*)")
    
    res = re.search(p, str)
    groups = res.groups()
    
    stateData = {
        'matchid':groups[0],
        'playerNb':int(groups[1]),
        'cellNb':int(groups[2]),
        'cellData':parseCellsState(groups[3]),
        'lineNb':int(groups[4]),
        'lineData':parseMovesState(groups[5])
    }
    
    return stateData