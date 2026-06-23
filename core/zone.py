# core/zone.py

def create_zone(bbox, padding=100):
    x1, y1, x2, y2 = bbox

    zx1 = x1 - padding
    zy1 = y1 - padding
    zx2 = x2 + padding
    zy2 = y2 + padding

    return (zx1, zy1, zx2, zy2)


#JUst oVerlap
def is_inside(box, zone):
    x1, y1, x2, y2 = box
    zx1, zy1, zx2, zy2 = zone

    # اگر overlap وجود داشته باشه
    if (x1 < zx2 and x2 > zx1 and
        y1 < zy2 and y2 > zy1):
        return True

    return False


# def is_inside(person_bbox, zone_bbox):
#     px1, py1, px2, py2 = person_bbox
#     zx1, zy1, zx2, zy2 = zone_bbox

#     return (
#         px1 >= zx1 and py1 >= zy1 and
#         px2 <= zx2 and py2 <= zy2
#     )