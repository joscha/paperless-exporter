from enum import IntEnum
from peewee import (
    SqliteDatabase,
    Field,
    Model,
    AutoField,
    IntegerField,
    CharField,
    BlobField,
    FloatField,
    DecimalField,
    ForeignKeyField,
    CompositeKey,
)
from datetime import datetime, timedelta, UTC

database = SqliteDatabase(None)


class DataType(IntEnum):
    DOCUMENT = 1
    RECEIPT = 2
    VIDEO = 3
    EMAIL = 4
    IMAGE = 5


class UnknownField(object):
    def __init__(self, *_, **__):
        pass


class DaysSinceYear2001(Field):
    field_type = "INTEGER"  # stored as an integer in the DB

    def db_value(self, value):
        raise NotImplementedError("DaysSinceYear2001 is read-only")

    def python_value(self, value):
        """Convert int → datetime."""
        if isinstance(value, float) or isinstance(value, int):
            # Create naive datetime first
            naive_dt = datetime(2001, 1, 1) + timedelta(seconds=value)
            # Then explicitly set it to UTC
            return naive_dt.replace(tzinfo=UTC)
        return value


class BaseModel(Model):
    class Meta:
        database = database


class Zautofill(BaseModel):
    zcustomitem = IntegerField(column_name="ZCUSTOMITEM", index=True, null=True)
    zdata = CharField(column_name="ZDATA", null=True)
    z_ent = IntegerField(column_name="Z_ENT", null=True)
    z_opt = IntegerField(column_name="Z_OPT", null=True)
    z_pk = AutoField(column_name="Z_PK", null=True)

    class Meta:
        table_name = "ZAUTOFILL"


class Zcategory(BaseModel):
    zname = CharField(column_name="ZNAME", null=True)
    zoriginaluid = CharField(column_name="ZORIGINALUID", null=True)
    z_ent = IntegerField(column_name="Z_ENT", null=True)
    z_opt = IntegerField(column_name="Z_OPT", null=True)
    z_pk = AutoField(column_name="Z_PK", null=True)

    def __str__(self):
        return self.zname

    class Meta:
        table_name = "ZCATEGORY"


class Zcollection(BaseModel):
    zname = CharField(column_name="ZNAME", null=True)
    zoriginaluid = CharField(column_name="ZORIGINALUID", null=True)
    parent = ForeignKeyField(
        "self", column_name="ZPARENT", index=True, null=True, backref="children"
    )
    zreportdata = BlobField(column_name="ZREPORTDATA", null=True)
    zsmartsearch = BlobField(column_name="ZSMARTSEARCH", null=True)
    zsortindex = IntegerField(column_name="ZSORTINDEX", null=True)
    ztype = IntegerField(column_name="ZTYPE", null=True)
    z_ent = IntegerField(column_name="Z_ENT", null=True)
    z_opt = IntegerField(column_name="Z_OPT", null=True)
    z_pk = AutoField(column_name="Z_PK", null=True)

    class Meta:
        table_name = "ZCOLLECTION"


class Zcustom3(BaseModel):
    zname = CharField(column_name="ZNAME", null=True)
    z_ent = IntegerField(column_name="Z_ENT", null=True)
    z_opt = IntegerField(column_name="Z_OPT", null=True)
    z_pk = AutoField(column_name="Z_PK", null=True)

    class Meta:
        table_name = "ZCUSTOM3"


class Zcustom4(BaseModel):
    zname = CharField(column_name="ZNAME", null=True)
    z_ent = IntegerField(column_name="Z_ENT", null=True)
    z_opt = IntegerField(column_name="Z_OPT", null=True)
    z_pk = AutoField(column_name="Z_PK", null=True)

    class Meta:
        table_name = "ZCUSTOM4"


class Zcustom5(BaseModel):
    zname = CharField(column_name="ZNAME", null=True)
    z_ent = IntegerField(column_name="Z_ENT", null=True)
    z_opt = IntegerField(column_name="Z_OPT", null=True)
    z_pk = AutoField(column_name="Z_PK", null=True)

    class Meta:
        table_name = "ZCUSTOM5"


class Zcustom6(BaseModel):
    zname = CharField(column_name="ZNAME", null=True)
    z_ent = IntegerField(column_name="Z_ENT", null=True)
    z_opt = IntegerField(column_name="Z_OPT", null=True)
    z_pk = AutoField(column_name="Z_PK", null=True)

    class Meta:
        table_name = "ZCUSTOM6"


class Zcustomitem(BaseModel):
    zcustomid = IntegerField(column_name="ZCUSTOMID", index=True, null=True)
    zname = CharField(column_name="ZNAME", null=True)
    ztype = IntegerField(column_name="ZTYPE", null=True)
    z_ent = IntegerField(column_name="Z_ENT", null=True)
    z_opt = IntegerField(column_name="Z_OPT", null=True)
    z_pk = AutoField(column_name="Z_PK", null=True)

    class Meta:
        table_name = "ZCUSTOMITEM"


class Zcustomreceiptitem(BaseModel):
    zcheckboxdata = IntegerField(column_name="ZCHECKBOXDATA", null=True)
    zdatedata = UnknownField(column_name="ZDATEDATA", null=True)  # TIMESTAMP
    zdecimaldata = DecimalField(column_name="ZDECIMALDATA", null=True)
    zintegerdata = IntegerField(column_name="ZINTEGERDATA", null=True)
    zreceipt = IntegerField(column_name="ZRECEIPT", index=True, null=True)
    zstringdata = CharField(column_name="ZSTRINGDATA", null=True)
    ztype = IntegerField(column_name="ZTYPE", index=True, null=True)
    z_ent = IntegerField(column_name="Z_ENT", null=True)
    z_opt = IntegerField(column_name="Z_OPT", null=True)
    z_pk = AutoField(column_name="Z_PK", null=True)

    class Meta:
        table_name = "ZCUSTOMRECEIPTITEM"


class Zdatatype(BaseModel):
    zfieldorderarray = BlobField(column_name="ZFIELDORDERARRAY", null=True)
    zname = CharField(column_name="ZNAME", null=True)
    ztypeid = IntegerField(column_name="ZTYPEID", index=True, null=True)
    z_ent = IntegerField(column_name="Z_ENT", null=True)
    z_opt = IntegerField(column_name="Z_OPT", null=True)
    z_pk = AutoField(column_name="Z_PK", null=True)

    def __str__(self):
        return self.zname

    class Meta:
        table_name = "ZDATATYPE"


class Zmerchant(BaseModel):
    zextensiblepropertiesdata = BlobField(
        column_name="ZEXTENSIBLEPROPERTIESDATA", null=True
    )
    zname = CharField(column_name="ZNAME", null=True)
    zoriginaluid = CharField(column_name="ZORIGINALUID", null=True)
    z_ent = IntegerField(column_name="Z_ENT", null=True)
    z_opt = IntegerField(column_name="Z_OPT", null=True)
    z_pk = AutoField(column_name="Z_PK", null=True)

    class Meta:
        table_name = "ZMERCHANT"


class Zmerchantinfo(BaseModel):
    zaddress = CharField(column_name="ZADDRESS", null=True)
    zmerchant = IntegerField(column_name="ZMERCHANT", index=True, null=True)
    znumber = CharField(column_name="ZNUMBER", null=True)
    z_ent = IntegerField(column_name="Z_ENT", null=True)
    z_opt = IntegerField(column_name="Z_OPT", null=True)
    z_pk = AutoField(column_name="Z_PK", null=True)

    class Meta:
        table_name = "ZMERCHANTINFO"


class Zpaymentmethod(BaseModel):
    zname = CharField(column_name="ZNAME", null=True)
    zoriginaluid = CharField(column_name="ZORIGINALUID", null=True)
    ztype = IntegerField(column_name="ZTYPE", null=True)
    z_ent = IntegerField(column_name="Z_ENT", null=True)
    z_opt = IntegerField(column_name="Z_OPT", null=True)
    z_pk = AutoField(column_name="Z_PK", null=True)

    def __str__(self):
        return self.zname

    class Meta:
        table_name = "ZPAYMENTMETHOD"


class Zsubcategory(BaseModel):
    zname = CharField(column_name="ZNAME", null=True)
    zoriginaluid = CharField(column_name="ZORIGINALUID", null=True)
    z_ent = IntegerField(column_name="Z_ENT", null=True)
    z_opt = IntegerField(column_name="Z_OPT", null=True)
    z_pk = AutoField(column_name="Z_PK", null=True)

    def __str__(self):
        return self.zname

    class Meta:
        table_name = "ZSUBCATEGORY"


class Zreceipt(BaseModel):
    zamount = FloatField(column_name="ZAMOUNT", null=True)
    zamountasstring = CharField(column_name="ZAMOUNTASSTRING", null=True)
    zcategory = ForeignKeyField(Zcategory, column_name="ZCATEGORY", index=True)
    zcustom1 = CharField(column_name="ZCUSTOM1", null=True)
    zcustom2 = CharField(column_name="ZCUSTOM2", null=True)
    zcustom3 = CharField(column_name="ZCUSTOM3", null=True)
    zcustom4 = CharField(column_name="ZCUSTOM4", null=True)
    zcustom5 = CharField(column_name="ZCUSTOM5", null=True)
    zcustom6 = CharField(column_name="ZCUSTOM6", null=True)
    zdatatype = ForeignKeyField(Zdatatype, column_name="ZDATATYPE", index=True)
    zdate = DaysSinceYear2001(column_name="ZDATE", null=True)  # TIMESTAMP
    zextensiblepropertiesdata = BlobField(
        column_name="ZEXTENSIBLEPROPERTIESDATA", null=True
    )
    zfilehash = CharField(column_name="ZFILEHASH", null=True)
    zimportdate = DaysSinceYear2001(column_name="ZIMPORTDATE", null=True)  # TIMESTAMP
    zinboxvalue = IntegerField(column_name="ZINBOXVALUE", null=True)
    zintrashvalue = IntegerField(column_name="ZINTRASHVALUE", null=True)
    zmerchant = CharField(column_name="ZMERCHANT", null=True)
    znotes = CharField(column_name="ZNOTES", null=True)
    znumpages = IntegerField(column_name="ZNUMPAGES", null=True)
    zocrattemptedvalue = IntegerField(column_name="ZOCRATTEMPTEDVALUE", null=True)
    zocrresult = CharField(column_name="ZOCRRESULT", null=True)
    zoriginalfilename = CharField(column_name="ZORIGINALFILENAME", null=True)
    zoriginaluid = CharField(column_name="ZORIGINALUID", null=True)
    zpath = CharField(column_name="ZPATH", null=True)
    zpaymentmethod = ForeignKeyField(
        Zpaymentmethod, column_name="ZPAYMENTMETHOD", index=True
    )
    zreimbursable = IntegerField(column_name="ZREIMBURSABLE", null=True)
    zshippingamount = FloatField(column_name="ZSHIPPINGAMOUNT", null=True)
    zshippingamountasstring = CharField(
        column_name="ZSHIPPINGAMOUNTASSTRING", null=True
    )
    zshippingamountstring = CharField(column_name="ZSHIPPINGAMOUNTSTRING", null=True)
    zsubcategory = ForeignKeyField(Zsubcategory, column_name="ZSUBCATEGORY", index=True)
    ztaxamount = FloatField(column_name="ZTAXAMOUNT", null=True)
    ztaxamount2 = FloatField(column_name="ZTAXAMOUNT2", null=True)
    ztaxamount2_asstring = CharField(column_name="ZTAXAMOUNT2ASSTRING", null=True)
    ztaxamountasstring = CharField(column_name="ZTAXAMOUNTASSTRING", null=True)
    ztaxamountstring2 = CharField(column_name="ZTAXAMOUNTSTRING2", null=True)
    zthumbnailpage = IntegerField(column_name="ZTHUMBNAILPAGE", null=True)
    zthumbnailpath = CharField(column_name="ZTHUMBNAILPATH", null=True)
    ztipamount = FloatField(column_name="ZTIPAMOUNT", null=True)
    ztipamountasstring = CharField(column_name="ZTIPAMOUNTASSTRING", null=True)
    ztipamountstring = CharField(column_name="ZTIPAMOUNTSTRING", null=True)
    z_ent = IntegerField(column_name="Z_ENT", null=True)
    z_opt = IntegerField(column_name="Z_OPT", null=True)
    z_pk = IntegerField(column_name="Z_PK", primary_key=True)

    class Meta:
        table_name = "ZRECEIPT"


class Zreport(BaseModel):
    zadditionalheadertext = CharField(column_name="ZADDITIONALHEADERTEXT", null=True)
    zcolumncategory = IntegerField(column_name="ZCOLUMNCATEGORY", null=True)
    zcolumncustom1 = IntegerField(column_name="ZCOLUMNCUSTOM1", null=True)
    zcolumncustom2 = IntegerField(column_name="ZCOLUMNCUSTOM2", null=True)
    zcolumncustom3 = IntegerField(column_name="ZCOLUMNCUSTOM3", null=True)
    zcolumnmerchant = IntegerField(column_name="ZCOLUMNMERCHANT", null=True)
    zcolumnnotes = IntegerField(column_name="ZCOLUMNNOTES", null=True)
    zcolumnpaymentmethod = IntegerField(column_name="ZCOLUMNPAYMENTMETHOD", null=True)
    zcolumntax = IntegerField(column_name="ZCOLUMNTAX", null=True)
    zextensiblepropertiesdata = BlobField(
        column_name="ZEXTENSIBLEPROPERTIESDATA", null=True
    )
    zfont = BlobField(column_name="ZFONT", null=True)
    zincludearchived = IntegerField(column_name="ZINCLUDEARCHIVED", null=True)
    zincludereceipts = IntegerField(column_name="ZINCLUDERECEIPTS", null=True)
    zname = CharField(column_name="ZNAME", null=True)
    zreporttitle = CharField(column_name="ZREPORTTITLE", null=True)
    zshrinkwide = IntegerField(column_name="ZSHRINKWIDE", null=True)
    zsmartsearch = BlobField(column_name="ZSMARTSEARCH", null=True)
    zsortby = IntegerField(column_name="ZSORTBY", null=True)
    zsubtotalby = IntegerField(column_name="ZSUBTOTALBY", null=True)
    ztabstops = BlobField(column_name="ZTABSTOPS", null=True)
    zwindowframestring = CharField(column_name="ZWINDOWFRAMESTRING", null=True)
    z_ent = IntegerField(column_name="Z_ENT", null=True)
    z_opt = IntegerField(column_name="Z_OPT", null=True)
    z_pk = AutoField(column_name="Z_PK", null=True)

    class Meta:
        table_name = "ZREPORT"


class Zsubitem(BaseModel):
    zamountasfloat = FloatField(column_name="ZAMOUNTASFLOAT", null=True)
    zamountasstring = CharField(column_name="ZAMOUNTASSTRING", null=True)
    zcategorymo = IntegerField(column_name="ZCATEGORYMO", index=True, null=True)
    zextensiblepropertiesdata = BlobField(
        column_name="ZEXTENSIBLEPROPERTIESDATA", null=True
    )
    zname = CharField(column_name="ZNAME", null=True)
    znote = CharField(column_name="ZNOTE", null=True)
    zoriginaluid = CharField(column_name="ZORIGINALUID", null=True)
    zreceipt = IntegerField(column_name="ZRECEIPT", index=True, null=True)
    zreimbursable = IntegerField(column_name="ZREIMBURSABLE", null=True)
    zshippingamount = FloatField(column_name="ZSHIPPINGAMOUNT", null=True)
    zshippingamountasstring = CharField(
        column_name="ZSHIPPINGAMOUNTASSTRING", null=True
    )
    zshippingamountstring = CharField(column_name="ZSHIPPINGAMOUNTSTRING", null=True)
    ztaxamount2 = FloatField(column_name="ZTAXAMOUNT2", null=True)
    ztaxamount2_asstring = CharField(column_name="ZTAXAMOUNT2ASSTRING", null=True)
    ztaxamountasfloat = FloatField(column_name="ZTAXAMOUNTASFLOAT", null=True)
    ztaxamountasstring = CharField(column_name="ZTAXAMOUNTASSTRING", null=True)
    ztaxamountstring2 = CharField(column_name="ZTAXAMOUNTSTRING2", null=True)
    ztipamount = FloatField(column_name="ZTIPAMOUNT", null=True)
    ztipamountasstring = CharField(column_name="ZTIPAMOUNTASSTRING", null=True)
    ztipamountstring = CharField(column_name="ZTIPAMOUNTSTRING", null=True)
    z_ent = IntegerField(column_name="Z_ENT", null=True)
    z_opt = IntegerField(column_name="Z_OPT", null=True)
    z_pk = AutoField(column_name="Z_PK", null=True)

    class Meta:
        table_name = "ZSUBITEM"


class Ztag(BaseModel):
    zname = CharField(column_name="ZNAME", null=True)
    z_ent = IntegerField(column_name="Z_ENT", null=True)
    z_opt = IntegerField(column_name="Z_OPT", null=True)
    z_pk = IntegerField(column_name="Z_PK", primary_key=True)

    class Meta:
        table_name = "ZTAG"


class ReceiptTag(BaseModel):
    receipt = ForeignKeyField(
        Zreceipt, column_name="Z_14RECEIPTS1", backref="receipt_tags"
    )
    tag = ForeignKeyField(Ztag, column_name="Z_18TAGS", backref="tag_receipts")

    class Meta:
        table_name = "Z_14TAGS"
        primary_key = False


class ReceiptCollection(BaseModel):
    receipt = ForeignKeyField(
        Zreceipt, column_name="Z_14RECEIPTS", backref="collections"
    )
    collection = ForeignKeyField(
        Zcollection, column_name="Z_3COLLECTIONS", null=True, backref="receipts"
    )

    class Meta:
        table_name = "Z_3RECEIPTS"
        primary_key = False


class Z8Datatypes(BaseModel):
    z_10_datatypes = IntegerField(column_name="Z_10DATATYPES", null=True)
    z_8_customitems = IntegerField(column_name="Z_8CUSTOMITEMS", null=True)

    class Meta:
        table_name = "Z_8DATATYPES"
        indexes = (
            (("z_10_datatypes", "z_8_customitems"), False),
            (("z_8_customitems", "z_10_datatypes"), True),
        )
        primary_key = CompositeKey("z_10_datatypes", "z_8_customitems")


class ZMetadata(BaseModel):
    z_plist = BlobField(column_name="Z_PLIST", null=True)
    z_uuid = CharField(column_name="Z_UUID", null=True)
    z_version = AutoField(column_name="Z_VERSION", null=True)

    class Meta:
        table_name = "Z_METADATA"


class ZModelcache(BaseModel):
    z_content = BlobField(column_name="Z_CONTENT", null=True)

    class Meta:
        table_name = "Z_MODELCACHE"
        primary_key = False


class ZPrimarykey(BaseModel):
    z_ent = AutoField(column_name="Z_ENT", null=True)
    z_max = IntegerField(column_name="Z_MAX", null=True)
    z_name = CharField(column_name="Z_NAME", null=True)
    z_super = IntegerField(column_name="Z_SUPER", null=True)

    class Meta:
        table_name = "Z_PRIMARYKEY"
