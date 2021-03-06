from flask import (
    Blueprint, flash, g, request, session, current_app, request, abort, json
)
from flaskr.keys.keys import (
    sign, verify, user_key_from_bytes, load_keys, encrypt
)
from ..utils import (
    generic_error_handler, gen_UUID, UUID_from_bytes, decode, encode, b64_decode, b64_encode
)
from flaskr.db.db import get_db
from struct import pack, unpack
from uuid import UUID

acme = Blueprint('acme', __name__)

SIGNATURE_BASE64_SIZE = 90
UUID_SIZE = 16
INTEGER_SIZE = 4
PRODUCT_SIZE = 4 + 16 + 4 + 4
ONE_HUNDRED_EUROS_IN_CENTS = 10000


@acme.route('/get-products', methods=['GET'])
def get_products():
    db = get_db()

    products = db.execute(
        'SELECT * FROM product'
    ).fetchall()

    # Converting to tag format
    encoded_prods = []
    for prod in products:
        code = UUID('{' + prod['code'] + '}')
        euros = int(prod['price'] // 100)
        cents = int(prod['price'] % 100)

        encoded_prods.append(
            b64_encode(
                pack('4s', encode('Acme')) +
                pack('16s', code.bytes) +
                pack('>i', euros) +
                pack('>i', cents) +
                pack('b', len(prod['prodName'])) +
                pack('35s', encode(prod['prodName']))
            )
        )

    # Appending signature
    encoded_prods = list(map(
        lambda prod:
            decode(
                prod + b64_encode(sign(
                    current_app.config['PRIVATE_KEY'],
                    prod
                )),
            ),
        encoded_prods
    ))

    return current_app.response_class(
        response=json.dumps(encoded_prods),
        status=200,
        mimetype='application/json'
    )


@acme.route('/get-transactions', methods=['POST'])
def get_transactions():
    db = get_db()

    content = request.data[: -SIGNATURE_BASE64_SIZE]
    signature = b64_decode(request.data[-SIGNATURE_BASE64_SIZE:])

    # Acme tag
    decoded_content = b64_decode(content)
    _ = decoded_content[0: INTEGER_SIZE]
    decoded_content = decoded_content[INTEGER_SIZE:]

    # Checking if User exists
    uuid = str(UUID_from_bytes(decoded_content))
    user = db.execute(
        'SELECT userPublicKey FROM user WHERE id = ?',
        (uuid, )
    ).fetchone()
    if user is None:
        abort(401)

    # Verifying User through signature
    if not verify(user_key_from_bytes(user['userPublicKey']),
                  signature,
                  content):
        abort(401)

    # Getting Transactions
    transactions = db.execute(
        'SELECT total, discounted, voucherID, created\
            FROM acmeTransaction WHERE ownerID = ?',
        (uuid, )
    ).fetchall()

    # Encrypting every single transaction
    content = b64_encode(encode(
        json.dumps({
            'transactions': [
                decode(b64_encode(encrypt(
                    encode(json.dumps({
                        'd': t['created'].strftime("%d-%m-%Y"),
                        't': t['total'],
                        'di': t['discounted'],
                        'v': t['voucherID'] is not None,
                    })),
                    user_key_from_bytes(user['userPublicKey'])
                )))
                for t in transactions
            ]
        })
    ))

    # Signing content
    final_content = decode(
        content + b64_encode(sign(
            current_app.config['PRIVATE_KEY'],
            content
        ))
    )

    return current_app.response_class(
        response=final_content,
        status=200,
        mimetype='application/json'
    )


@acme.route('/get-vouchers', methods=['POST'])
def get_vouchers():
    db = get_db()

    content = request.data[: -SIGNATURE_BASE64_SIZE]
    signature = b64_decode(request.data[-SIGNATURE_BASE64_SIZE:])

    # Acme tag
    decoded_content = b64_decode(content)
    _ = decoded_content[0: INTEGER_SIZE]
    decoded_content = decoded_content[INTEGER_SIZE:]

    # Checking if User exists
    uuid = str(UUID_from_bytes(decoded_content))
    user = db.execute(
        'SELECT userPublicKey, accumulatedDiscount FROM user WHERE id = ?',
        (uuid, )
    ).fetchone()
    if user is None:
        abort(401)

    # Verifying User through signature
    if not verify(user_key_from_bytes(user['userPublicKey']),
                  signature,
                  content):
        abort(401)

    # Getting vouchers
    vouchers = db.execute(
        'SELECT id FROM voucher WHERE ownerID = ? AND used = 0',
        (uuid, )
    ).fetchall()

    # Encrypting every single voucher and the discount
    content = b64_encode(encode(
        json.dumps({
            'vouchers': [
                decode(b64_encode(encrypt(
                    encode(str(row['id'])),
                    user_key_from_bytes(user['userPublicKey'])
                )))
                for row in vouchers
            ],
            'discount': decode(b64_encode(encrypt(
                encode(str(user['accumulatedDiscount'])),
                user_key_from_bytes(user['userPublicKey'])
            )))
        })
    ))

    # Signing content
    final_content = decode(
        content + b64_encode(sign(
            current_app.config['PRIVATE_KEY'],
            content
        ))
    )

    return current_app.response_class(
        response=final_content,
        status=200,
        mimetype='application/json'
    )


@acme.route('/checkout', methods=['POST'])
def checkout():
    db = get_db()

    content = request.data[: -SIGNATURE_BASE64_SIZE]
    decoded_content = b64_decode(content)
    signature = b64_decode(request.data[-SIGNATURE_BASE64_SIZE:])

    # Acme tag
    _ = decoded_content[0: INTEGER_SIZE]
    decoded_content = decoded_content[INTEGER_SIZE:]

    # Checking if User exists
    uuid = str(UUID_from_bytes(decoded_content[:UUID_SIZE]))
    decoded_content = decoded_content[UUID_SIZE:]
    user = db.execute(
        'SELECT userPublicKey, accumulatedDiscount FROM user WHERE id = ?',
        (uuid, )
    ).fetchone()
    if user is None:
        abort(401)

    # Verifying User through signature
    if not verify(user_key_from_bytes(user['userPublicKey']),
                  signature,
                  content):
        abort(401)

    # Extract discount
    discont = unpack('b', decoded_content[-1:])[0]
    decoded_content = decoded_content[:-1]

    # Extract voucher
    has_voucher = unpack('b', decoded_content[-1:])[0]
    decoded_content = decoded_content[:-1]

    if has_voucher:
        voucher_id = str(UUID_from_bytes(decoded_content[-UUID_SIZE:]))
        decoded_content = decoded_content[:-UUID_SIZE]

    # Extracting products and total
    products = {}
    total = 0
    for i in range(0, len(decoded_content) // PRODUCT_SIZE):
        base = i * PRODUCT_SIZE
        prod = decoded_content[base: base + PRODUCT_SIZE]

        # Acme tag
        _ = prod[0: INTEGER_SIZE]
        prod = prod[INTEGER_SIZE:]

        # Product Code
        code = str(UUID_from_bytes(prod[:UUID_SIZE]))
        prod = prod[UUID_SIZE:]
        if code in products:
            products[code] += 1
        else:
            products[code] = 1

        # Prices, maybe do validation
        price = prod[2 * INTEGER_SIZE:]

        # Validating product and getting total
        dbProd = db.execute(
            'SELECT price FROM product WHERE code = ?',
            (code, )
        ).fetchone()

        if dbProd is None:
            abort(400)
        else:
            total += dbProd['price']

    # Creating new Vouchers
    for _ in range(0, total // ONE_HUNDRED_EUROS_IN_CENTS):
        db.execute(
            'INSERT INTO voucher (id, ownerID) VALUES (?, ?)',
            (str(gen_UUID()), uuid)
        )

    # Processing voucher
    discont_accumulator = 0
    if has_voucher:
        discont_accumulator = 0.15

        # Checking if voucher is valid
        if db.execute(
            'SELECT * FROM voucher WHERE id = ? AND used = 0',
            (voucher_id, )
        ).fetchone() is None:
            abort(400)

        # Updating voucher
        db.execute(
            'UPDATE voucher SET used = 1 WHERE id = ?',
            (voucher_id, )
        )

    # Updating discont
    discounted = 0
    acc_discont = user['accumulatedDiscount'] + \
        round(total * discont_accumulator)

    if discont:
        if user['accumulatedDiscount'] > total:
            acc_discont = acc_discont - total
            discounted = total
        else:
            discounted = user['accumulatedDiscount']
            acc_discont = round(total * discont_accumulator)

        db.execute(
            'UPDATE user SET accumulatedDiscount = ? WHERE id = ?',
            (acc_discont, uuid,)
        )
    else:
        db.execute(
            'UPDATE user SET accumulatedDiscount = ? WHERE id = ?',
            (acc_discont, uuid)
        )

    # Creating transaction
    trans_exec = db.cursor()
    if has_voucher:
        trans_exec.execute(
            'INSERT INTO acmeTransaction (ownerID, total,\
                discounted, voucherID) VALUES (?, ?, ?, ?)',
            (uuid, total, discounted, voucher_id)
        )
    else:
        trans_exec.execute(
            'INSERT INTO acmeTransaction (ownerID, total,\
                discounted) VALUES (?, ?, ?)',
            (uuid, total, discounted)
        )
    transaction_id = trans_exec.lastrowid

    # Creating Transaction - Products association
    for prod in products:
        db.execute(
            'INSERT INTO transactionProdcuts (transactionID,\
                productID, quantity) VALUES (?, ?, ?)',
            (transaction_id, prod, products[prod])
        )

    # Commiting everything!
    db.commit()

    return current_app.response_class(
        response=str(total-discounted),
        status=200,
        mimetype='application/json'
    )

# Customized Error handlers
@acme.errorhandler(401)
def handle_unauthorized_request(e):
    return generic_error_handler(
        401, "Attempt of unauthorized access to information."
    )


@acme.errorhandler(400)
def handle_bad_request(e):
    return generic_error_handler(
        400, "Invalid data passed in request"
    )
