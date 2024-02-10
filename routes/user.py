from flask import Blueprint, jsonify, request, make_response
import pymysql
import pymysql.cursors
import re
from apscheduler.schedulers.background import BackgroundScheduler
from trie import TrieNode, Trie
from werkzeug.security import generate_password_hash
from db_manager import DBManager
from responseFormatter import convert_keys_to_camel_case

user_bp = Blueprint('user_bp', __name__)
db_manager = DBManager()

# trie = Trie()

# def update_trie():
#     conn = db_manager.get_db_connection()
#     try:
#         cursor = conn.cursor()
#         cursor.execute("SELECT vendor_name FROM PublicVendor")
#         for row in cursor.fetchall():
#             trie.insert(row['vendor_name'].lower())
#     finally:
#         conn.close()

# scheduler = BackgroundScheduler()
# scheduler.add_job(func=update_trie, trigger="interval", hours=1) # Update every hour
# scheduler.start()

# @user_bp.route('/autocomplete', methods=['GET'])
# def autocomplete():
#     prefix = request.args.get('prefix', '')
#     suggestions = trie.autocomplete(prefix)
#     return jsonify(suggestions)

@user_bp.route('/user/<requested_username>', methods=['GET'])
def get_user_public_profile_by_username(requested_username):
    """Get a user's public profile"""
    requester_user_id = request.cookies.get('userId')
    conn = db_manager.get_db_connection()
    cursor = conn.cursor()

    # Get user_id
    cursor.execute("""SELECT id FROM User WHERE username = %s""", (requested_username))
    requested_user_id = cursor.fetchone()['id']

    # Fetch user details
    cursor.execute("""
        SELECT full_name, username, current_company, linkedin_url, bio
        FROM User
        WHERE id = %s
    """, (requested_user_id,))
    user_details = cursor.fetchone()

    # Fetch associated vendor IDs
    cursor.execute("""
        SELECT vendor_id
        FROM UserPublicVendor
        WHERE user_id = %s
    """, (requested_user_id,))
    vendor_ids = cursor.fetchall()
    
    # Convert vendor IDs to vendor names and check endorsements
    vendors_with_endorsements = []
    for vendor in vendor_ids:
        cursor.execute("""
            SELECT vendor_name
            FROM PublicVendor
            WHERE id = %s
        """, (vendor['vendor_id'],))
        vendor_name = cursor.fetchone()

        # Check for endorsement
        cursor.execute("""
            SELECT COUNT(*) AS endorsement_count
            FROM UserPublicVendorEndorsement
            WHERE endorser_user_id = %s AND vendor_id = %s
        """, (requester_user_id, vendor['vendor_id']))
        endorsement = cursor.fetchone()['endorsement_count'] > 0

        if vendor_name:
            vendors_with_endorsements.append({
                'vendor_name': vendor_name['vendor_name'],
                'endorsed_by_requester': endorsement
            })
    
    cursor.close()
    conn.close()

    user_details = convert_keys_to_camel_case(user_details)
    vendors_with_endorsements = [convert_keys_to_camel_case(item) for item in vendors_with_endorsements]

    return jsonify({'userDetails': user_details, 'vendors': vendors_with_endorsements})

@user_bp.route('/editProfile', methods=['PUT'])
def edit_profile():
    try:
        data = request.json
        user_id = request.cookies.get('userId')
        new_first_name = data.get('firstName')
        new_last_name = data.get('lastName')
        new_email = data.get('email')
        new_password = data.get('password')  # Assuming password change is allowed
        new_tech_stack = set(data.get('techstack', []))  # List of new vendor names

        if not user_id:
            return jsonify({"error": "User ID is required"}), 400

        conn = db_manager.get_db_connection()
        cursor = conn.cursor()

        # Update user information
        cursor.execute("""
            UPDATE User SET first_name = COALESCE(%s, first_name), 
                            last_name = COALESCE(%s, last_name),
                            email = COALESCE(%s, email),
                            password = COALESCE(%s, password),
                            update_time = CURRENT_TIMESTAMP(3)
            WHERE id = %s
        """, (new_first_name, new_last_name, new_email, new_password, user_id))

        # Update tech stack
        if new_tech_stack:
            # Fetch current tech stack of the user
            cursor.execute("""
                SELECT v.vendor_name FROM PublicVendor AS v
                JOIN UserPublicVendor AS uv ON v.id = uv.vendor_id
                WHERE uv.user_id = %s
            """, (user_id,))
            current_tech_stack = {row['vendor_name'] for row in cursor.fetchall()}

            # Tech stack to add
            for tech in new_tech_stack - current_tech_stack:
                cursor.execute("SELECT id FROM PublicVendor WHERE vendor_name = %s", (tech,))
                vendor = cursor.fetchone()
                if vendor:
                    cursor.execute("""
                        INSERT INTO UserPublicVendor (user_id, vendor_id) 
                        VALUES (%s, %s)
                    """, (user_id, vendor['id']))

            # Tech stack to remove
            for tech in current_tech_stack - new_tech_stack:
                cursor.execute("SELECT id FROM PublicVendor WHERE vendor_name = %s", (tech,))
                vendor = cursor.fetchone()
                if vendor:
                    cursor.execute("""
                        DELETE FROM UserPublicVendor 
                        WHERE user_id = %s AND vendor_id = %s
                    """, (user_id, vendor['id']))

        conn.commit()

    except pymysql.MySQLError as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": "Profile updated successfully"}), 200


@user_bp.route('/endorse', methods = ['PUT'])
def endorse_user():
    try:
        data = request.json
        endorser_user_id = request.cookies.get('userId')
        endorsee_username = data.get('endorseeUsername')
        vendor_id = data.get('vendorId')

        if not endorser_user_id and endorsee_username and vendor_id:
            return jsonify({"error": "Endorser User Id, Endorsee User Id, Vendor Id is required"}), 400

        cursor.execute("""SELECT id FROM User WHERE username = %s""", (endorsee_username))
        endorsee_user_id = cursor.fetchone()['id']

        conn = db_manager.get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """INSERT INTO UserPublicVendorEndorsement (endorser_user_id, endorsee_user_id, vendor_id) VALUES (%s, %s, %s)""",
            (endorser_user_id, endorsee_user_id, vendor_id)
        )

        conn.commit()

    except pymysql.MySQLError as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": "Profile endorsed successfully"}), 200

