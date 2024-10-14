import os
import secrets
import sqlite3
import json
import logging

from flask import Flask, render_template, request, session, render_template_string, redirect, url_for
from webauthn import (
    generate_authentication_options,
    options_to_json,
    verify_authentication_response,
    generate_registration_options,
    verify_registration_response,
)
from webauthn.helpers.structs import (
    PublicKeyCredentialRequestOptions,
    PublicKeyCredentialCreationOptions,
    AuthenticatorSelectionCriteria,
    UserVerificationRequirement,
    PublicKeyCredentialRpEntity,
    PublicKeyCredentialUserEntity,
    AttestationConveyancePreference,
    AuthenticationCredential,
    RegistrationCredential,
)
from webauthn.helpers import bytes_to_base64url
from dataclasses import asdict

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
# app.secret_key = 'your-secret-key'  # Replace with a secure secret key

# Set up logging
logging.basicConfig(level=logging.INFO, filename='server.log', format='%(asctime)s %(message)s')

DATABASE = 'passkeys.db'
RP_ID = 'gatepass.local'
ORIGIN = 'https://gatepass.local:5000'

def init_db():
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                credential_id TEXT UNIQUE NOT NULL,
                public_key TEXT NOT NULL,
                validated INTEGER NOT NULL
            )
        ''')
        conn.commit()
        conn.close()
        logging.info('Initialized database.')

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    return conn

@app.route('/open_gate')
def open_gate():
    logging.info('Accessed /open_gate page.')
    if 'user_id' in session:
        user_id = session['user_id']
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT validated, public_key FROM users WHERE id=?', (user_id,))
        row = c.fetchone()
        conn.close()
        if row:
            validated, public_key = row
            if validated:
                title = 'Success'
            else:
                title = 'Pending'
            return render_template_string('''
                <html>
                    <head><title>{{ title }}</title></head>
                    <body>
                        <h1>{{ title }}</h1>
                        <p>Public Key: {{ public_key }}</p>
                    </body>
                </html>
            ''', title=title, public_key=public_key)
    return redirect(url_for('login'))

@app.route('/login')
def login():
    logging.info('Initiating login process.')
    # Generate authentication options
    options = generate_authentication_options(rp_id=RP_ID)
    return render_template('login.html', options=options_to_json(options))

@app.route('/verify-login', methods=['POST'])
def verify_login():
    logging.info('Verifying login.')
    try:
        data = request.get_json()
        credential = AuthenticationCredential.parse_raw(json.dumps(data))
        stored_challenge = session.pop('current_authentication_challenge', None)
        if not stored_challenge:
            logging.error('No stored challenge found in session.')
            return 'Failed', 400

        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT id, public_key FROM users WHERE credential_id=?', (credential.raw_id,))
        row = c.fetchone()
        if not row:
            logging.info('Unknown credential ID.')
            return 'Unknown credential ID', 400
        user_id, public_key = row

        verification = verify_authentication_response(
            credential=credential,
            expected_challenge=stored_challenge,
            expected_origin=ORIGIN,
            expected_rp_id=RP_ID,
            credential_public_key=public_key,
            credential_current_sign_count=0,
            require_user_verification=False,
        )
        session['user_id'] = user_id
        logging.info(f'User {user_id} authenticated successfully.')
        return 'OK', 200
    except Exception as e:
        logging.error(f'Authentication failed: {e}')
        return 'Failed', 400

@app.route('/register')
def register():
    logging.info('Initiating registration process.')
    # Generate registration options
    options = generate_registration_options(
        rp_id=RP_ID,
        rp_name='GatePass',
        user_name='GatePass User',
    )
    session['current_registration_challenge'] = options.challenge
    session['user_id'] = options.user.id.hex()
    return render_template('register.html', options=options_to_json(options))

@app.route('/verify-registration', methods=['POST'])
def verify_registration():
    logging.info('Verifying registration.')
    try:
        credential = request.get_json()
        logging.info(f'Received registration data: {credential}')
        stored_challenge = session.pop('current_registration_challenge', None)
        if not stored_challenge:
            logging.error('No stored challenge found in session.')
            return 'Failed', 400

        verification = verify_registration_response(
            credential=credential,
            expected_challenge=stored_challenge,
            expected_origin=ORIGIN,
            expected_rp_id=RP_ID,
            require_user_verification=False,
        )
        public_key = verification.credential_public_key
        credential_id = verification.credential_id

        conn = get_db_connection()
        c = conn.cursor()
        c.execute('INSERT INTO users (username, credential_id, public_key, validated) VALUES (?, ?, ?, ?)',
                  ('user@example.com', credential_id, public_key, 0))
        conn.commit()
        user_id = c.lastrowid
        conn.close()
        session['user_id'] = user_id
        logging.info(f'User {user_id} registered with credential ID {credential_id}.')
        return 'OK', 200
    except Exception as e:
        logging.error(f'Registration failed: {e}')
        return 'Failed', 400

if __name__ == '__main__':
    init_db()
    app.run(debug=True, ssl_context=('cert.pem', 'key.pem'))
