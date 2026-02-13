"""Comprehensive API test script for RuoYi-FastAPI backend."""
import json
import sys
import httpx
import redis
import asyncio
import pymysql

BASE = "http://localhost:8090"
REDIS_URL = "redis://:123456@localhost:6379/0"
DB_CONFIG = {"host": "localhost", "port": 3306, "user": "root", "password": "123456", "database": "ruoyi_fast", "charset": "utf8mb4"}


def cleanup_test_data():
    """Remove residual test data from previous runs."""
    conn = pymysql.connect(**DB_CONFIG)
    try:
        cur = conn.cursor()
        # Clean user test data
        cur.execute("SELECT user_id FROM sys_user WHERE user_name='testuser001'")
        for row in cur.fetchall():
            uid = row[0]
            cur.execute("DELETE FROM sys_user_role WHERE user_id=%s", (uid,))
            cur.execute("DELETE FROM sys_user_post WHERE user_id=%s", (uid,))
        cur.execute("DELETE FROM sys_user WHERE user_name='testuser001'")
        # Clean config test data
        cur.execute("DELETE FROM sys_config WHERE config_key='test.config.key'")
        # Clean dict type test data
        cur.execute("DELETE FROM sys_dict_data WHERE dict_type='test_dict_type'")
        cur.execute("DELETE FROM sys_dict_type WHERE dict_type='test_dict_type'")
        conn.commit()
        print("[CLEANUP] Residual test data removed.")
    finally:
        conn.close()

passed = 0
failed = 0
errors = []


def report(name: str, ok: bool, detail: str = ""):
    global passed, failed
    if ok:
        passed += 1
        print(f"  [PASS] {name}")
    else:
        failed += 1
        errors.append((name, detail))
        print(f"  [FAIL] {name} -> {detail}")


async def main():
    global passed, failed

    cleanup_test_data()

    r = redis.Redis.from_url(REDIS_URL, decode_responses=True)

    async with httpx.AsyncClient(base_url=BASE, timeout=15) as c:
        token = ""

        # ============================================================
        print("\n=== 1. Auth Endpoints ===")
        # ============================================================

        # 1.1 GET /captchaImage
        resp = await c.get("/captchaImage")
        data = resp.json()
        report("GET /captchaImage", data.get("code") == 200 and data.get("uuid"))
        captcha_uuid = data.get("uuid", "")

        # Read captcha answer from Redis
        captcha_code = r.get(f"captcha_codes:{captcha_uuid}") or ""

        # 1.2 POST /login
        resp = await c.post("/login", json={
            "username": "admin",
            "password": "admin123",
            "code": captcha_code,
            "uuid": captcha_uuid,
        })
        data = resp.json()
        login_ok = data.get("code") == 200 and data.get("token")
        report("POST /login", login_ok, str(data.get("msg", "")))
        if login_ok:
            token = data["token"]

        if not token:
            print("\n*** Login failed, cannot continue tests ***")
            return

        headers = {"Authorization": f"Bearer {token}"}

        # 1.3 GET /getInfo
        resp = await c.get("/getInfo", headers=headers)
        data = resp.json()
        report("GET /getInfo", data.get("code") == 200 and data.get("user"), str(data.get("msg", "")))

        # 1.4 GET /getRouters
        resp = await c.get("/getRouters", headers=headers)
        data = resp.json()
        report("GET /getRouters", data.get("code") == 200 and isinstance(data.get("data"), list), str(data.get("msg", "")))

        # ============================================================
        print("\n=== 2. User Management ===")
        # ============================================================

        # 2.1 GET /system/user/list
        resp = await c.get("/system/user/list", headers=headers, params={"pageNum": 1, "pageSize": 10})
        data = resp.json()
        report("GET /system/user/list", data.get("code") == 200 and "total" in data, str(data.get("msg", "")))

        # 2.2 GET /system/user/ (add info: posts + roles)
        resp = await c.get("/system/user/", headers=headers)
        data = resp.json()
        report("GET /system/user/ (add info)", data.get("code") == 200, str(data.get("msg", "")))

        # 2.3 GET /system/user/{userId}
        resp = await c.get("/system/user/1", headers=headers)
        data = resp.json()
        report("GET /system/user/1", data.get("code") == 200 and data.get("data"), str(data.get("msg", "")))

        # 2.4 POST /system/user (add user)
        resp = await c.post("/system/user", headers=headers, json={
            "user_name": "testuser001",
            "nick_name": "测试用户",
            "dept_id": 100,
            "password": "test123456",
            "phonenumber": "13800000001",
            "email": "test@test.com",
            "sex": "0",
            "status": "0",
            "role_ids": [2],
            "post_ids": [1],
        })
        data = resp.json()
        report("POST /system/user (add)", data.get("code") == 200, str(data.get("msg", "")))

        # Small delay to ensure DB commit completes
        await asyncio.sleep(0.3)

        # Find the new user ID
        resp = await c.get("/system/user/list", headers=headers, params={"pageNum": 1, "pageSize": 10, "userName": "testuser001"})
        test_user_id = None
        list_data = resp.json()
        if list_data.get("rows"):
            test_user_id = list_data["rows"][0].get("userId")

        # 2.5 PUT /system/user (update)
        if test_user_id:
            resp = await c.put("/system/user", headers=headers, json={
                "user_id": test_user_id,
                "nick_name": "测试用户改名",
                "dept_id": 100,
                "phonenumber": "13800000002",
                "email": "test2@test.com",
                "sex": "1",
                "status": "0",
                "role_ids": [2],
                "post_ids": [1],
            })
            data = resp.json()
            report("PUT /system/user (update)", data.get("code") == 200, str(data.get("msg", "")))
        else:
            report("PUT /system/user (update)", False, "no test user created")

        # 2.6 PUT /system/user/resetPwd
        if test_user_id:
            resp = await c.put("/system/user/resetPwd", headers=headers, json={
                "user_id": test_user_id,
                "password": "newpass123",
            })
            data = resp.json()
            report("PUT /system/user/resetPwd", data.get("code") == 200, str(data.get("msg", "")))

        # 2.7 PUT /system/user/changeStatus
        if test_user_id:
            resp = await c.put("/system/user/changeStatus", headers=headers, json={
                "user_id": test_user_id,
                "status": "1",
            })
            data = resp.json()
            report("PUT /system/user/changeStatus", data.get("code") == 200, str(data.get("msg", "")))

        # 2.8 GET /system/user/authRole/{userId}
        if test_user_id:
            resp = await c.get(f"/system/user/authRole/{test_user_id}", headers=headers)
            data = resp.json()
            report("GET /system/user/authRole/{id}", data.get("code") == 200, str(data.get("msg", "")))

        # 2.9 PUT /system/user/authRole
        if test_user_id:
            resp = await c.put("/system/user/authRole", headers=headers, params={"userId": test_user_id, "roleIds": "2"})
            data = resp.json()
            report("PUT /system/user/authRole", data.get("code") == 200, str(data.get("msg", "")))

        # 2.10 GET /system/user/deptTree
        resp = await c.get("/system/user/deptTree", headers=headers)
        data = resp.json()
        report("GET /system/user/deptTree", data.get("code") == 200, str(data.get("msg", "")))

        # 2.11 GET /system/user/profile
        resp = await c.get("/system/user/profile", headers=headers)
        data = resp.json()
        report("GET /system/user/profile", data.get("code") == 200 and data.get("data"), str(data.get("msg", "")))

        # 2.12 PUT /system/user/profile
        resp = await c.put("/system/user/profile", headers=headers, json={
            "nick_name": "管理员",
            "phonenumber": "15888888888",
            "email": "ry@163.com",
            "sex": "1",
        })
        data = resp.json()
        report("PUT /system/user/profile", data.get("code") == 200, str(data.get("msg", "")))

        # 2.13 POST /system/user/export
        resp = await c.post("/system/user/export", headers=headers)
        report("POST /system/user/export", resp.status_code == 200 and "spreadsheet" in resp.headers.get("content-type", ""), f"status={resp.status_code}, ct={resp.headers.get('content-type','')}")

        # 2.14 DELETE /system/user/{userIds}
        if test_user_id:
            resp = await c.delete(f"/system/user/{test_user_id}", headers=headers)
            data = resp.json()
            report("DELETE /system/user/{id}", data.get("code") == 200, str(data.get("msg", "")))

        # ============================================================
        print("\n=== 3. Role Management ===")
        # ============================================================

        resp = await c.get("/system/role/list", headers=headers, params={"pageNum": 1, "pageSize": 10})
        data = resp.json()
        report("GET /system/role/list", data.get("code") == 200 and "total" in data, str(data.get("msg", "")))

        resp = await c.get("/system/role/optionselect", headers=headers)
        data = resp.json()
        report("GET /system/role/optionselect", data.get("code") == 200, str(data.get("msg", "")))

        resp = await c.get("/system/role/2", headers=headers)
        data = resp.json()
        report("GET /system/role/2", data.get("code") == 200 and data.get("data"), str(data.get("msg", "")))

        # Add role
        resp = await c.post("/system/role", headers=headers, json={
            "role_name": "测试角色",
            "role_key": "testRole",
            "role_sort": 99,
            "status": "0",
            "menu_ids": [1, 2],
            "remark": "test",
        })
        data = resp.json()
        report("POST /system/role (add)", data.get("code") == 200, str(data.get("msg", "")))

        # Find test role
        resp = await c.get("/system/role/list", headers=headers, params={"pageNum": 1, "pageSize": 10, "roleName": "测试角色"})
        test_role_id = None
        list_data = resp.json()
        if list_data.get("rows"):
            test_role_id = list_data["rows"][0].get("roleId")

        if test_role_id:
            resp = await c.put("/system/role", headers=headers, json={
                "role_id": test_role_id,
                "role_name": "测试角色改名",
                "role_key": "testRole",
                "role_sort": 99,
                "status": "0",
                "menu_ids": [1],
            })
            data = resp.json()
            report("PUT /system/role (update)", data.get("code") == 200, str(data.get("msg", "")))

            resp = await c.put("/system/role/changeStatus", headers=headers, json={
                "role_id": test_role_id, "status": "1",
            })
            report("PUT /system/role/changeStatus", resp.json().get("code") == 200, str(resp.json().get("msg", "")))

            resp = await c.put("/system/role/dataScope", headers=headers, json={
                "role_id": test_role_id, "data_scope": "1", "dept_ids": [],
            })
            report("PUT /system/role/dataScope", resp.json().get("code") == 200, str(resp.json().get("msg", "")))

        resp = await c.get("/system/role/deptTree/2", headers=headers)
        data = resp.json()
        report("GET /system/role/deptTree/{id}", data.get("code") == 200, str(data.get("msg", "")))

        resp = await c.get("/system/role/authUser/allocatedList", headers=headers, params={"roleId": 2, "pageNum": 1, "pageSize": 10})
        data = resp.json()
        report("GET /system/role/authUser/allocatedList", data.get("code") == 200, str(data.get("msg", "")))

        resp = await c.get("/system/role/authUser/unallocatedList", headers=headers, params={"roleId": 2, "pageNum": 1, "pageSize": 10})
        data = resp.json()
        report("GET /system/role/authUser/unallocatedList", data.get("code") == 200, str(data.get("msg", "")))

        resp = await c.post("/system/role/export", headers=headers)
        report("POST /system/role/export", resp.status_code == 200 and "spreadsheet" in resp.headers.get("content-type", ""), f"status={resp.status_code}, ct={resp.headers.get('content-type','')}")

        if test_role_id:
            resp = await c.delete(f"/system/role/{test_role_id}", headers=headers)
            report("DELETE /system/role/{id}", resp.json().get("code") == 200, str(resp.json().get("msg", "")))

        # ============================================================
        print("\n=== 4. Menu Management ===")
        # ============================================================

        resp = await c.get("/system/menu/list", headers=headers)
        data = resp.json()
        report("GET /system/menu/list", data.get("code") == 200 and isinstance(data.get("data"), list), str(data.get("msg", "")))

        resp = await c.get("/system/menu/treeselect", headers=headers)
        data = resp.json()
        report("GET /system/menu/treeselect", data.get("code") == 200, str(data.get("msg", "")))

        resp = await c.get("/system/menu/roleMenuTreeselect/2", headers=headers)
        data = resp.json()
        report("GET /system/menu/roleMenuTreeselect/2", data.get("code") == 200, str(data.get("msg", "")))

        resp = await c.get("/system/menu/1", headers=headers)
        data = resp.json()
        report("GET /system/menu/1", data.get("code") == 200, str(data.get("msg", "")))

        # Add menu
        resp = await c.post("/system/menu", headers=headers, json={
            "menu_name": "测试菜单",
            "parent_id": 0,
            "order_num": 99,
            "path": "testmenu",
            "menu_type": "M",
            "visible": "0",
            "status": "0",
            "icon": "star",
        })
        data = resp.json()
        report("POST /system/menu (add)", data.get("code") == 200, str(data.get("msg", "")))

        # Find test menu
        resp = await c.get("/system/menu/list", headers=headers, params={"menuName": "测试菜单"})
        test_menu_id = None
        mlist = resp.json().get("data", [])
        for m in mlist:
            if m.get("menuName") == "测试菜单":
                test_menu_id = m.get("menuId")
                break

        if test_menu_id:
            resp = await c.put("/system/menu", headers=headers, json={
                "menu_id": test_menu_id,
                "menu_name": "测试菜单改名",
                "parent_id": 0,
                "order_num": 99,
                "path": "testmenu",
                "menu_type": "M",
                "visible": "0",
                "status": "0",
            })
            report("PUT /system/menu (update)", resp.json().get("code") == 200, str(resp.json().get("msg", "")))

            resp = await c.delete(f"/system/menu/{test_menu_id}", headers=headers)
            report("DELETE /system/menu/{id}", resp.json().get("code") == 200, str(resp.json().get("msg", "")))

        # ============================================================
        print("\n=== 5. Dept Management ===")
        # ============================================================

        resp = await c.get("/system/dept/list", headers=headers)
        data = resp.json()
        report("GET /system/dept/list", data.get("code") == 200, str(data.get("msg", "")))

        resp = await c.get("/system/dept/list/exclude/100", headers=headers)
        data = resp.json()
        report("GET /system/dept/list/exclude/100", data.get("code") == 200, str(data.get("msg", "")))

        resp = await c.get("/system/dept/100", headers=headers)
        data = resp.json()
        report("GET /system/dept/100", data.get("code") == 200, str(data.get("msg", "")))

        resp = await c.post("/system/dept", headers=headers, json={
            "parent_id": 100,
            "dept_name": "测试部门",
            "order_num": 99,
            "leader": "测试",
            "phone": "13800000000",
            "email": "test@test.com",
            "status": "0",
        })
        data = resp.json()
        report("POST /system/dept (add)", data.get("code") == 200, str(data.get("msg", "")))

        # Find test dept
        resp = await c.get("/system/dept/list", headers=headers, params={"deptName": "测试部门"})
        test_dept_id = None
        dlist = resp.json().get("data", [])
        for d in dlist:
            if d.get("deptName") == "测试部门":
                test_dept_id = d.get("deptId")
                break

        if test_dept_id:
            resp = await c.put("/system/dept", headers=headers, json={
                "dept_id": test_dept_id,
                "parent_id": 100,
                "dept_name": "测试部门改名",
                "order_num": 99,
                "status": "0",
            })
            report("PUT /system/dept (update)", resp.json().get("code") == 200, str(resp.json().get("msg", "")))

            resp = await c.delete(f"/system/dept/{test_dept_id}", headers=headers)
            report("DELETE /system/dept/{id}", resp.json().get("code") == 200, str(resp.json().get("msg", "")))

        # ============================================================
        print("\n=== 6. Post Management ===")
        # ============================================================

        resp = await c.get("/system/post/list", headers=headers, params={"pageNum": 1, "pageSize": 10})
        data = resp.json()
        report("GET /system/post/list", data.get("code") == 200 and "total" in data, str(data.get("msg", "")))

        resp = await c.get("/system/post/optionselect", headers=headers)
        data = resp.json()
        report("GET /system/post/optionselect", data.get("code") == 200, str(data.get("msg", "")))

        resp = await c.get("/system/post/1", headers=headers)
        data = resp.json()
        report("GET /system/post/1", data.get("code") == 200, str(data.get("msg", "")))

        resp = await c.post("/system/post", headers=headers, json={
            "post_code": "test_post",
            "post_name": "测试岗位",
            "post_sort": 99,
            "status": "0",
        })
        data = resp.json()
        report("POST /system/post (add)", data.get("code") == 200, str(data.get("msg", "")))

        # Find and cleanup
        resp = await c.get("/system/post/list", headers=headers, params={"pageNum": 1, "pageSize": 50, "postName": "测试岗位"})
        test_post_id = None
        prows = resp.json().get("rows", [])
        for p in prows:
            if p.get("postName") == "测试岗位":
                test_post_id = p.get("postId")
                break

        if test_post_id:
            resp = await c.put("/system/post", headers=headers, json={
                "post_id": test_post_id,
                "post_code": "test_post",
                "post_name": "测试岗位改名",
                "post_sort": 99,
                "status": "0",
            })
            report("PUT /system/post (update)", resp.json().get("code") == 200, str(resp.json().get("msg", "")))

            resp = await c.delete(f"/system/post/{test_post_id}", headers=headers)
            report("DELETE /system/post/{id}", resp.json().get("code") == 200, str(resp.json().get("msg", "")))

        resp = await c.post("/system/post/export", headers=headers)
        report("POST /system/post/export", resp.status_code == 200 and "spreadsheet" in resp.headers.get("content-type", ""), f"status={resp.status_code}, ct={resp.headers.get('content-type','')}")

        # ============================================================
        print("\n=== 7. Dict Type Management ===")
        # ============================================================

        resp = await c.get("/system/dict/type/list", headers=headers, params={"pageNum": 1, "pageSize": 10})
        data = resp.json()
        report("GET /system/dict/type/list", data.get("code") == 200 and "total" in data, str(data.get("msg", "")))

        resp = await c.get("/system/dict/type/optionselect", headers=headers)
        data = resp.json()
        report("GET /system/dict/type/optionselect", data.get("code") == 200, str(data.get("msg", "")))

        # Get first dict type id
        resp = await c.get("/system/dict/type/list", headers=headers, params={"pageNum": 1, "pageSize": 1})
        first_dict_id = None
        rows = resp.json().get("rows", [])
        if rows:
            first_dict_id = rows[0].get("dictId")

        if first_dict_id:
            resp = await c.get(f"/system/dict/type/{first_dict_id}", headers=headers)
            report(f"GET /system/dict/type/{first_dict_id}", resp.json().get("code") == 200, str(resp.json().get("msg", "")))

        resp = await c.post("/system/dict/type", headers=headers, json={
            "dict_name": "测试字典",
            "dict_type": "test_dict_type",
            "status": "0",
            "remark": "test",
        })
        data = resp.json()
        report("POST /system/dict/type (add)", data.get("code") == 200, str(data.get("msg", "")))

        # Find test dict type
        resp = await c.get("/system/dict/type/list", headers=headers, params={"pageNum": 1, "pageSize": 50, "dictType": "test_dict_type"})
        test_dict_type_id = None
        for row in resp.json().get("rows", []):
            if row.get("dictType") == "test_dict_type":
                test_dict_type_id = row.get("dictId")
                break

        if test_dict_type_id:
            resp = await c.put("/system/dict/type", headers=headers, json={
                "dict_id": test_dict_type_id,
                "dict_name": "测试字典改名",
                "dict_type": "test_dict_type",
                "status": "0",
            })
            report("PUT /system/dict/type (update)", resp.json().get("code") == 200, str(resp.json().get("msg", "")))

            resp = await c.delete(f"/system/dict/type/{test_dict_type_id}", headers=headers)
            report("DELETE /system/dict/type/{id}", resp.json().get("code") == 200, str(resp.json().get("msg", "")))

        resp = await c.post("/system/dict/type/export", headers=headers)
        report("POST /system/dict/type/export", resp.status_code == 200 and "spreadsheet" in resp.headers.get("content-type", ""), f"status={resp.status_code}")

        # ============================================================
        print("\n=== 8. Dict Data Management ===")
        # ============================================================

        resp = await c.get("/system/dict/data/list", headers=headers, params={"pageNum": 1, "pageSize": 10, "dictType": "sys_user_sex"})
        data = resp.json()
        report("GET /system/dict/data/list", data.get("code") == 200 and "total" in data, str(data.get("msg", "")))

        resp = await c.get("/system/dict/data/type/sys_user_sex", headers=headers)
        data = resp.json()
        report("GET /system/dict/data/type/sys_user_sex", data.get("code") == 200, str(data.get("msg", "")))

        # Get first dict data code
        resp = await c.get("/system/dict/data/list", headers=headers, params={"pageNum": 1, "pageSize": 1, "dictType": "sys_user_sex"})
        first_dict_code = None
        rows = resp.json().get("rows", [])
        if rows:
            first_dict_code = rows[0].get("dictCode")

        if first_dict_code:
            resp = await c.get(f"/system/dict/data/{first_dict_code}", headers=headers)
            report(f"GET /system/dict/data/{first_dict_code}", resp.json().get("code") == 200, str(resp.json().get("msg", "")))

        resp = await c.post("/system/dict/data", headers=headers, json={
            "dict_type": "sys_user_sex",
            "dict_label": "测试",
            "dict_value": "9",
            "dict_sort": 99,
            "status": "0",
        })
        data = resp.json()
        report("POST /system/dict/data (add)", data.get("code") == 200, str(data.get("msg", "")))

        # Find test data
        resp = await c.get("/system/dict/data/list", headers=headers, params={"pageNum": 1, "pageSize": 50, "dictType": "sys_user_sex", "dictLabel": "测试"})
        test_dict_code = None
        for row in resp.json().get("rows", []):
            if row.get("dictLabel") == "测试":
                test_dict_code = row.get("dictCode")
                break

        if test_dict_code:
            resp = await c.put("/system/dict/data", headers=headers, json={
                "dict_code": test_dict_code,
                "dict_type": "sys_user_sex",
                "dict_label": "测试改名",
                "dict_value": "9",
                "dict_sort": 99,
                "status": "0",
            })
            report("PUT /system/dict/data (update)", resp.json().get("code") == 200, str(resp.json().get("msg", "")))

            resp = await c.delete(f"/system/dict/data/{test_dict_code}", headers=headers)
            report("DELETE /system/dict/data/{id}", resp.json().get("code") == 200, str(resp.json().get("msg", "")))

        resp = await c.post("/system/dict/data/export", headers=headers)
        report("POST /system/dict/data/export", resp.status_code == 200 and "spreadsheet" in resp.headers.get("content-type", ""), f"status={resp.status_code}")

        # ============================================================
        print("\n=== 9. Config Management ===")
        # ============================================================

        resp = await c.get("/system/config/list", headers=headers, params={"pageNum": 1, "pageSize": 10})
        data = resp.json()
        report("GET /system/config/list", data.get("code") == 200 and "total" in data, str(data.get("msg", "")))

        resp = await c.get("/system/config/configKey/sys.index.skinName", headers=headers)
        data = resp.json()
        report("GET /system/config/configKey/{key}", data.get("code") == 200, str(data.get("msg", "")))

        resp = await c.get("/system/config/1", headers=headers)
        data = resp.json()
        report("GET /system/config/1", data.get("code") == 200, str(data.get("msg", "")))

        resp = await c.post("/system/config", headers=headers, json={
            "config_name": "测试参数",
            "config_key": "test.config.key",
            "config_value": "test_value",
            "config_type": "N",
        })
        data = resp.json()
        report("POST /system/config (add)", data.get("code") == 200, str(data.get("msg", "")))

        # Find test config
        resp = await c.get("/system/config/list", headers=headers, params={"pageNum": 1, "pageSize": 50, "configKey": "test.config.key"})
        test_config_id = None
        for row in resp.json().get("rows", []):
            if row.get("configKey") == "test.config.key":
                test_config_id = row.get("configId")
                break

        if test_config_id:
            resp = await c.put("/system/config", headers=headers, json={
                "config_id": test_config_id,
                "config_name": "测试参数改名",
                "config_key": "test.config.key",
                "config_value": "new_value",
                "config_type": "N",
            })
            report("PUT /system/config (update)", resp.json().get("code") == 200, str(resp.json().get("msg", "")))

            resp = await c.delete(f"/system/config/{test_config_id}", headers=headers)
            report("DELETE /system/config/{id}", resp.json().get("code") == 200, str(resp.json().get("msg", "")))

        resp = await c.post("/system/config/export", headers=headers)
        report("POST /system/config/export", resp.status_code == 200 and "spreadsheet" in resp.headers.get("content-type", ""), f"status={resp.status_code}")

        # ============================================================
        print("\n=== 10. Notice Management ===")
        # ============================================================

        resp = await c.get("/system/notice/list", headers=headers, params={"pageNum": 1, "pageSize": 10})
        data = resp.json()
        report("GET /system/notice/list", data.get("code") == 200 and "total" in data, str(data.get("msg", "")))

        resp = await c.get("/system/notice/1", headers=headers)
        data = resp.json()
        report("GET /system/notice/1", data.get("code") == 200, str(data.get("msg", "")))

        resp = await c.post("/system/notice", headers=headers, json={
            "notice_title": "测试通知",
            "notice_type": "1",
            "notice_content": "测试内容",
            "status": "0",
        })
        data = resp.json()
        report("POST /system/notice (add)", data.get("code") == 200, str(data.get("msg", "")))

        resp = await c.get("/system/notice/list", headers=headers, params={"pageNum": 1, "pageSize": 50, "noticeTitle": "测试通知"})
        test_notice_id = None
        for row in resp.json().get("rows", []):
            if row.get("noticeTitle") == "测试通知":
                test_notice_id = row.get("noticeId")
                break

        if test_notice_id:
            resp = await c.put("/system/notice", headers=headers, json={
                "notice_id": test_notice_id,
                "notice_title": "测试通知改名",
                "notice_type": "1",
                "notice_content": "改了",
                "status": "0",
            })
            report("PUT /system/notice (update)", resp.json().get("code") == 200, str(resp.json().get("msg", "")))

            resp = await c.delete(f"/system/notice/{test_notice_id}", headers=headers)
            report("DELETE /system/notice/{id}", resp.json().get("code") == 200, str(resp.json().get("msg", "")))

        # ============================================================
        print("\n=== 11. Oper Log ===")
        # ============================================================

        resp = await c.get("/monitor/operlog/list", headers=headers, params={"pageNum": 1, "pageSize": 10})
        data = resp.json()
        report("GET /monitor/operlog/list", data.get("code") == 200 and "total" in data, str(data.get("msg", "")))

        resp = await c.post("/monitor/operlog/export", headers=headers)
        report("POST /monitor/operlog/export", resp.status_code == 200, f"status={resp.status_code}, type={resp.headers.get('content-type','')}")

        # ============================================================
        print("\n=== 12. Login Info ===")
        # ============================================================

        resp = await c.get("/monitor/logininfor/list", headers=headers, params={"pageNum": 1, "pageSize": 10})
        data = resp.json()
        report("GET /monitor/logininfor/list", data.get("code") == 200 and "total" in data, str(data.get("msg", "")))

        resp = await c.post("/monitor/logininfor/export", headers=headers)
        report("POST /monitor/logininfor/export", resp.status_code == 200, f"status={resp.status_code}")

        resp = await c.get("/monitor/logininfor/unlock/admin", headers=headers)
        data = resp.json()
        report("GET /monitor/logininfor/unlock/admin", data.get("code") == 200, str(data.get("msg", "")))

        # ============================================================
        print("\n=== 13. Online Users ===")
        # ============================================================

        resp = await c.get("/monitor/online/list", headers=headers)
        data = resp.json()
        report("GET /monitor/online/list", data.get("code") == 200 and "total" in data, str(data.get("msg", "")))

        # ============================================================
        print("\n=== 14. Server Monitor ===")
        # ============================================================

        resp = await c.get("/monitor/server", headers=headers)
        data = resp.json()
        report("GET /monitor/server", data.get("code") == 200 and data.get("data"), str(data.get("msg", "")))

        # ============================================================
        print("\n=== 15. Cache Monitor ===")
        # ============================================================

        resp = await c.get("/monitor/cache", headers=headers)
        data = resp.json()
        report("GET /monitor/cache", data.get("code") == 200, str(data.get("msg", "")))

        resp = await c.get("/monitor/cache/getNames", headers=headers)
        data = resp.json()
        report("GET /monitor/cache/getNames", data.get("code") == 200, str(data.get("msg", "")))

        resp = await c.get("/monitor/cache/getKeys/sys_dict", headers=headers)
        data = resp.json()
        report("GET /monitor/cache/getKeys/sys_dict", data.get("code") == 200, str(data.get("msg", "")))

        # ============================================================
        print("\n=== 16. Code Gen ===")
        # ============================================================

        resp = await c.get("/tool/gen/db/list", headers=headers, params={"pageNum": 1, "pageSize": 10})
        data = resp.json()
        report("GET /tool/gen/db/list", data.get("code") == 200 and "total" in data, str(data.get("msg", "")))

        resp = await c.get("/tool/gen/list", headers=headers, params={"pageNum": 1, "pageSize": 10})
        data = resp.json()
        report("GET /tool/gen/list", data.get("code") == 200, str(data.get("msg", "")))

        # ============================================================
        print("\n=== 17. Common ===")
        # ============================================================

        resp = await c.get("/health")
        data = resp.json()
        report("GET /health", data.get("status") == "ok", "")

        # ============================================================
        # Logout last
        # ============================================================
        print("\n=== 18. Logout ===")
        resp = await c.post("/logout", headers=headers)
        data = resp.json()
        report("POST /logout", data.get("code") == 200, str(data.get("msg", "")))

    r.close()

    # ============================================================
    print("\n" + "=" * 60)
    print(f"TOTAL: {passed + failed}  |  PASSED: {passed}  |  FAILED: {failed}")
    print("=" * 60)

    if errors:
        print("\nFailed tests:")
        for name, detail in errors:
            print(f"  - {name}: {detail}")

    return failed == 0


if __name__ == "__main__":
    ok = asyncio.run(main())
    sys.exit(0 if ok else 1)
