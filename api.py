from random import randint # noqa

from flask import Flask, request, jsonify
from flask_restful import Resource, Api
import psycopg2
import psycopg2.extras
from twilio.rest import TwilioRestClient

from config import constants_sql, settings


app = Flask(__name__)
app.config.from_object('config')

api = Api(app)

conn = psycopg2.connect(
    database=settings.DATABASE_NAME,
    user=settings.DATABASE_USER,
    password=settings.DATABASE_PASSWORD,
    host=settings.DATABASE_HOST,
    port=settings.DATABASE_PORT,
)

cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

ACCOUNT_SID = settings.TWILIO_ACCOUNT_SID
AUTH_TOKEN = settings.TWILIO_AUTH_TOKEN

client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)


def is_request_valid(request): # noqa
    if request.url.startswith('http://') and 'localhost' not in request.url:
        return None
    try:
        request_packet = request.get_json(force=True)
    except:
        return None
    token = request_packet.pop('token', None)
    if not token:
        return None
    sql_dict = {'token': token}
    cur.execute(constants_sql.CHECK_TOKEN, sql_dict)
    if not cur.fetchone()[0]:
        return None
    return request_packet


class CheckCardStatus(Resource): # noqa
    def get(self): # noqa
        request_packet = is_request_valid(request)
        if not request_packet:
            return jsonify(status='invalid_request')
        # TODO - Need to remove any spaces or dashes from the card_number
        #        and check the lenght as well.
        if len(request_packet) == 1 and 'card_number' in request_packet:
            sql_dict = {'card_number': request_packet['card_number']}
            cur.execute(constants_sql.GET_GIFT_CARD_INFO, sql_dict)
            gift_card_fetched = cur.fetchone()
            if gift_card_fetched:
                if gift_card_fetched['date_redeemed']:
                    return jsonify(
                        card_number=sql_dict['card_number'],
                        status='valid_redeemed',
                    )
                else:
                    return jsonify(
                        card_number=sql_dict['card_number'],
                        status='valid_not_redeemed',
                    )
            else:
                return jsonify(
                    card_number=sql_dict['card_number'],
                    status='invalid_card',
                )
        else:
            return jsonify(status='invalid_request')


class SendValidationCode(Resource): # noqa
    def get(self): # noqa
        request_packet = is_request_valid(request)
        if not request_packet:
            return jsonify(status='invalid_request')
        # TODO - Need to clean mobile number and make sure we have
        #        10 digits, etc...
        if len(request_packet) == 1 and 'mobile_number' in request_packet:
            mobile_number = request_packet['mobile_number']
            validation_code = ''.join(
                ["%s" % randint(0, 9)
                    for num in range(0, settings.VALIDATION_CODE_LENGTH)]
            )
            message = client.messages.create(
                to=mobile_number,
                from_=settings.TWILIO_FROM_NUMBER,
                body="NovitaCare Validation Code: %s" % validation_code
            )
            app.logger.debug(message)
            return jsonify(
                mobile_number=mobile_number,
                validation_code=validation_code
            )
        else:
            return jsonify(status='invalid_request')


class CreateUser(Resource): # noqa
    pass


# TODO: Need to create a database logger to keep all request/responses...

api.add_resource(CheckCardStatus, '/check_card_status', methods=['GET'])
api.add_resource(SendValidationCode, '/send_validation_code', methods=['GET'])
api.add_resource(CreateUser, '/create_user', methods=['GET'])

if __name__ == '__main__':
    app.run(debug=settings.DEBUG)
