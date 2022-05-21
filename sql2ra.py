import radb
import radb.ast
import radb.parse


def Translate(sqlparsed):
    sql_code = clean_up(sqlparsed)
    ra_code = ""
    if sql_code["select"] == "*":
        if sql_code["where"] == "":
            ra_code = select_star(sql_code["from"])
        else:
            ra_code = select_star_where(sql_code["from"], sql_code["where"])
    else:
        if sql_code["where"] == "":
            ra_code = project(sql_code["select"], sql_code["from"])

        else:
            ra_code = project_where(sql_code["select"], sql_code["from"],sql_code["where"])

    return radb.parse.one_statement_from_string(ra_code + ";")  # changed whitespaces, what does it do?


def clean_up(sqlparsed):

    line = str(sqlparsed).replace("; ", " ").split()
    line.remove("distinct")
    Lst = [[], [], []]
    index = 0
    for word in line:
        if word == "select":
            continue
        if word == "from" or word == "where":
            index += 1
            continue
        Lst[index].append(word)

    for i in Lst:
        i = Lst.index(i)
        Lst[i] = " ".join(Lst[i])

    args = {
        "select": Lst[0],
        "from": Lst[1],
        "where": Lst[2],
    }

    return args


def select_star(from_args):
    if "," in from_args:

        ra_select = cross(from_args.split(","))
        #print(ra_select)
    else:
        ra_select = from_args

    return ra_select


def cross(from_args):
    ra_cross = ""
    for table in from_args[1:]:
        if ra_cross == "":
            ra_cross = f"{from_args[from_args.index(table) - 1]} \cross {table}"
        else:
            ra_cross = f"{ra_cross} \cross {table}"

    return ra_cross


def rename(table, alias):
    return f"\\rename_{{{alias}: *}} {table}"


def select_star_where(from_args, where_args):
    if "," in from_args:
        ra_cross = cross(from_args.split(","))
        ra_select_where = f"\select_{{{where_args}}}({ra_cross})"
    else:
        ra_select_where = f"\select_{{{where_args}}}({from_args})"

    return ra_select_where


def project(select_args, from_args):
    ra_project = ""
    rename_list = []

    if "," in from_args:
        for arg in from_args.split(", "):
            if " " in arg:
                table, alias = arg.split(" ")
                rename_list.append(rename(table, alias))
            else:
                rename_list.append(arg)

        ra_project = f"\project_{{{select_args}}}({cross(rename_list)})"

    else:
        if " " in from_args:
            table, alias = from_args.split(" ")
            rename_list.append(rename(table, alias))
            # print('down')
            # print(rename(table, alias))
            # print(rename_list)
            ra_project = f"\project_{{{select_args}}}({rename(table, alias)})"
            #print(ra_project)
        else:
            ra_project = f"\project_{{{select_args}}}({from_args})"

    return ra_project


def project_where(select_args,from_args,where_args):
    ra_project = ''
    rename_list = []

    if ',' in from_args:
        from_args_list = from_args.split(', ')
        for arg in from_args_list:
            if ' ' in arg:
                table,alias = arg.split(' ')
                rename_list.append(rename(table,alias))
            else:
                rename_list.append(arg)

            ra_project = f"\project_{{{select_args}}}(\select_{{{where_args}}}({cross(rename_list)}))"
            #print(ra_project)
            
    else:
        
        if ' ' in from_args:
            table,alias = from_args.split(' ')                           #Editied
            ra_project = f"\project_{{{select_args}}}(\select_{{{where_args}}}({rename(table,alias)}))" #or .split()

        else:
            ra_project = f"\project_{{{select_args}}}(\select_{{{where_args}}}({from_args}))"

        return ra_project
