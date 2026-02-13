"""System-wide constants matching RuoYi conventions."""


# User status
class UserStatus:
    OK = "0"  # Active
    DISABLE = "1"  # Disabled


# Common status
class CommonStatus:
    OK = "0"  # Normal
    DISABLE = "1"  # Disabled


# Delete flag
class DelFlag:
    EXIST = "0"  # Exists
    DELETED = "2"  # Deleted


# Menu type
class MenuType:
    DIRECTORY = "M"  # Directory
    MENU = "C"  # Menu
    BUTTON = "F"  # Button


# Data scope
class DataScope:
    ALL = "1"  # All data
    CUSTOM = "2"  # Custom data scope
    DEPT = "3"  # Department data
    DEPT_AND_CHILD = "4"  # Department and child data
    SELF = "5"  # Self only


# Business operation type
class BusinessType:
    OTHER = 0
    INSERT = 1
    UPDATE = 2
    DELETE = 3
    GRANT = 4
    EXPORT = 5
    IMPORT = 6
    FORCE = 7
    GENCODE = 8
    CLEAN = 9


# Operation status
class OperStatus:
    SUCCESS = 0
    FAIL = 1


# Yes/No
class YesNo:
    YES = "Y"
    NO = "N"


# User type
class UserType:
    SYS = "00"  # System user


# Notice type
class NoticeType:
    NOTICE = "1"  # Notice
    BULLETIN = "2"  # Bulletin


# Redis key prefixes
LOGIN_TOKEN_KEY = "login_tokens:"
CAPTCHA_CODE_KEY = "captcha_codes:"
SYS_DICT_KEY = "sys_dict:"
SYS_CONFIG_KEY = "sys_config:"
PWD_ERR_CNT_KEY = "pwd_err_cnt:"
REPEAT_SUBMIT_KEY = "repeat_submit:"

# Super admin role key
SUPER_ADMIN = "admin"
