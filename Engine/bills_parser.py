from enum import Enum

BillType = Enum('BillType', 'Electricity Water Arnona_TelAviv Arnona_Rishon Gas Unsupported')


def parse_bill_raw(text, btype):
    if btype == BillType.Electricity:
        client_id, date = Electricity(text)
    elif btype == BillType.Gas:
        client_id, date = gas(text)
    elif btype == BillType.Water:
        client_id, date = mey_avivim(text)
    elif btype == BillType.Arnona_Rishon:
        client_id, date = arnona_rishon(text)
    elif btype == BillType.Arnona_TelAviv:
        client_id, date = arnona_tel_aviv(text)
    else:
        client_id, date = "Unsupported", "Unsupported"

    # print("Bill type is: " + btype)
    # print("id is: " + client_id)
    # print("date is: " + date)

    return client_id, date


def arnona_tel_aviv(txt):
    client_id_idx = txt.find("מספר חשבון הלקותח / ")
    client_id_idx += len("מספר חשבון הלקותח / ")
    client_id_idx_start = len(txt[client_id_idx]) - len(txt[client_id_idx].lstrip())
    client_id_idx_start += client_id_idx
    client_id_idx_end = min(txt.find(" ", client_id_idx_start), txt.find("\n", client_id_idx_start))

    date_idx = txt.find("לתקופה")
    date_idx += len("לתקופה")
    date_idx_start = date_idx
    date_idx_end = txt.find("\n", date_idx_start)

    client_id = txt[client_id_idx_start: client_id_idx_end]
    date = txt[date_idx_start: date_idx_end]

    return client_id, date


def arnona_rishon(txt):
    print(txt)
    return "Unsupported", "Unsupported"


def gas(txt):
    return "Unsupported", "Unsupported"


def Electricity(txt):
    client_id_idx = txt.find("חוזה:")
    client_id_idx += len("חוזה:")
    client_id_idx_start = len(txt[client_id_idx]) - len(txt[client_id_idx].lstrip())
    client_id_idx_start += client_id_idx
    client_id_idx_end = min(txt.find(" ", client_id_idx_start), txt.find("\n", client_id_idx_start))

    date_idx = txt.find("מ-")
    date_idx += len("מ-")
    date_idx_start = date_idx
    date_idx_end = txt.find("\n", date_idx_start)

    client_id = txt[client_id_idx_start: client_id_idx_end]
    date = txt[date_idx_start: date_idx_end]

    return client_id, date


def mey_avivim(text):
    start_idx = text.find('שם הלקוח')
    end_idx = text.find('\r\n', start_idx)
    start_idx += len('שם הלקוח')
    name = text[start_idx:end_idx]

    #print("client name:" + name)

    return text


def identify_bill_type(txt):
    result = BillType.Unsupported

    if "החשמל" in txt:
        result = BillType.Electricity
    elif "הגז" in txt:
        result = BillType.Gas
    elif "והנכס" in txt:
        result = BillType.Water
    elif "תל אביב" in txt and "ארנונה" in txt:
        result = BillType.Arnona_TelAviv
    elif "לציון" in txt and "ארנונה" in txt:
        result = BillType.Arnona_Rishon

    return result
