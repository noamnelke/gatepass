from flask import (
    Blueprint,
    render_template,
    render_template_string,
    request,
    session,
    redirect,
    url_for,
)
from webauthn import (
    base64url_to_bytes,
    generate_authentication_options,
    options_to_json,
    verify_authentication_response,
    generate_registration_options,
    verify_registration_response,
)
import logging
from . import models as db
from config import Config

bp = Blueprint("main", __name__)


# Pages

@bp.route("/")
def index():
    logging.info("Accessed / page.")
    return render_template("index.html")


@bp.route("/register")
def register():
    logging.info("Initiating registration process.")

    # Generate registration options
    options = generate_registration_options(
        rp_id=Config.RP_ID,
        rp_name="GatePass",
        user_name=Config.USER_ID,
    )
    session["current_registration_challenge"] = options.challenge
    return render_template("register.html", options=options_to_json(options))


@bp.route("/reg_success/<int:user_id>")
def reg_success(user_id):
    logging.info(f"Registration successful for user {user_id}.")
    return render_template("reg_success.html", user_id=user_id, origin=Config.ORIGIN)


@bp.route("/logout")
def logout():
    logging.info("Logging out.")
    session.clear()
    return redirect(url_for("main.index"))


# Admin pages

@bp.route("/update/<int:user_id>")
def update(user_id):
    if "is_admin" not in session:
        return login()

    logging.info(f"Update user {user_id}.")
    user = db.get_user(user_id)
    return render_template("update.html", user=user)


# API endpoints

@bp.route("/open", methods=["POST"])
def open():
    logging.info("Accessed /open page.")
    if "validated" not in session:
        ret = {
            "error": "not_authenticated",
            "options": options_to_json(generate_auth_options()),
        }
        return ret, 401
    # Handle unauthorized / unverified users
    return "OK", 200


@bp.route("/verify-login", methods=["POST"])
def verify_login():
    logging.info("Verifying login.")
    try:
        credential = request.get_json()
        logging.info(f"Received credential: {credential}")
        stored_challenge = session.pop("current_authentication_challenge", None)
        if not stored_challenge:
            logging.error("No stored challenge found in session.")
            return "Failed", 400

        user = db.get_user_by_credential_id(base64url_to_bytes(credential["rawId"]))

        verify_authentication_response(
            credential=credential,
            expected_challenge=stored_challenge,
            expected_origin=Config.ORIGIN,
            expected_rp_id=Config.RP_ID,
            credential_public_key=user["public_key"],
            credential_current_sign_count=0,
            require_user_verification=False,
        )

        session["user_id"] = user["id"]
        if user["validated"]:
            session["validated"] = True
        else:
            session.pop("validated", None)

        if user["admin"]:
            session["is_admin"] = True
        else:
            session.pop("is_admin", None)

        logging.info(f"User authenticated successfully. user={user}")
        return "OK", 200
    except Exception as e:
        logging.error(f"Authentication failed: {e}")
        return "Failed", 400


@bp.route("/verify-registration", methods=["POST"])
def verify_registration():
    logging.info("Verifying registration.")
    try:
        registration_request = request.get_json()
        credential = registration_request["credential"]
        building = registration_request["building"]
        apartment = registration_request["apartment"]
        name = registration_request["name"]
        logging.info(
            f"Received registration data: {credential}\nbuilding: {building}\napartment: {apartment}\nname: {name}"
        )

        stored_challenge = session.pop("current_registration_challenge", None)
        if not stored_challenge:
            logging.error("No stored challenge found in session.")
            return "Failed", 400

        verification = verify_registration_response(
            credential=credential,
            expected_challenge=stored_challenge,
            expected_origin=Config.ORIGIN,
            expected_rp_id=Config.RP_ID,
            require_user_verification=False,
        )
        public_key = verification.credential_public_key
        credential_id = verification.credential_id

        user_id = db.create_user(credential_id, public_key, building, apartment, name)
        logging.info(
            f"User {user_id} registered with credential ID {credential_id.hex()}."
        )
        return {"user_id": user_id}, 200
    except Exception as e:
        logging.error(f"Registration failed: {e}")
        return "Failed", 400


@bp.route("/update_user", methods=["POST"])
def update_user():
    logging.info("Updating user.")
    if "is_admin" not in session:
        logging.error("User is not an admin.")
        return "Failed", 400

    try:
        user = request.get_json()
        db.update_user(user)
        logging.info(f"User updated. user={user}")
        return "OK", 200
    except Exception as e:
        logging.error(f"Update failed: {e}")
        return "Failed", 400


# Helper functions

def generate_auth_options():
    options = generate_authentication_options(rp_id=Config.RP_ID)
    session["current_authentication_challenge"] = options.challenge
    return options


def login():
    logging.info("Initiating login process.")
    options = generate_auth_options()
    id = session.get("user_id")
    return render_template("login.html", options=options_to_json(options), id=id)
