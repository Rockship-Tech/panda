from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from system import model_base
from system import schema_validator
from system.responses import Responses, SuccessResponse, ErrorResponse

# from services.cvparser import parseCV
from services.s3 import upload_file_to_s3
from services.candidates import Candidates as candidatesService
import logging
import uuid
import os
from dotenv import load_dotenv, find_dotenv

candidates = Blueprint("candidates", __name__, url_prefix="/candidates")
load_dotenv(find_dotenv(), override=True)


@candidates.route("/input-cv", methods=["POST"])
def input_cv():
    try:
        # key, file = request.files.items()[0]
        if "cv_file" not in request.files:
            return ErrorResponse("/input-cv").bad_request_response(
                "CV file is required"
            )
        file = request.files["cv_file"]
        # Check if a file is selected
        if file.filename == "":
            return ErrorResponse("/input-cv").bad_request_response(
                "CV file is required 2"
            )

        # Create the "CVs" directory if it doesn't exist
        if not os.path.exists("CVs"):
            os.makedirs("CVs")

        # Save the file to the server
        file.save(os.path.join("CVs", file.filename))

        # CVjson = parseCV(file)

        # updateCandidate(CVjson)

        # update to S3
        # Save the file to S3
        bucket_name = os.getenv("BUCKET_NAME")
        s3_filename = os.getenv("CVS_PATH") + file.filename
        filepath = "CVs/" + file.filename
        data = open(filepath, "rb")
        upload_file_to_s3(data, bucket_name, s3_filename)

        # clean up the file
        os.remove(filepath)
        # Return a success response indicating the CV was successfully processed
        return SuccessResponse("/input-cv").generate_response(
            "CV has been uploaded", 200
        )
    except Exception as e:
        print(e)
        return ErrorResponse("/input-cv").internal_server_error_response()


@candidates.route("/<candidateId>", methods=["PUT"])
def update_candidate(candidateId):
    try:
        request_data = request.json

        with model_base.get_db() as db:
            candidate_services = candidatesService(db)
            candidates = candidate_services.get_candidate_by_id(
                uuid.UUID(request_data["id"])
            )
            if not candidates:
                return ErrorResponse("/candidates/").not_found_response()
            updated_candidate = candidate_services.update_candidate(
                uuid.UUID(candidateId), request_data
            )
            if not updated_candidate:
                return ErrorResponse("/candidates/").internal_server_error_response()
            return SuccessResponse("/candidates/").generate_response(
                updated_candidate.display(), 200
            )

    except Exception as e:
        print(e)
        return ErrorResponse("/candidates/").internal_server_error_response()


@candidates.route("/<candidateId>", methods=["DELETE"])
def delete_candidate(candidateId):
    try:
        with model_base.get_db() as db:
            candidate_services = candidatesService(db)
            deleted = candidate_services.delete_candidate(uuid.UUID(candidateId))
            if not deleted:
                return ErrorResponse("/candidates/").internal_server_error_response()
            return SuccessResponse("/candidates/").generate_response(
                {"message": "Candidate deleted successfully"}, 200
            )
    except Exception as e:
        print(e)
        return ErrorResponse("/candidates/").internal_server_error_response()


@candidates.route("/<candidateId>/make-appointment", methods=["POST"])
def make_appointment():
    pass


@candidates.route("/<candidateId>/send-welcome-email", methods=["POST"])
def send_welcome_email():
    pass


@candidates.route("/", methods=["GET"])
def get_candidates():
    query_params = schema_validator.parse_query_params(request.args)
    validation_error = schema_validator.valid_params(query_params)
    if validation_error:
        return ErrorResponse(context="/candidates/").bad_request_response(
            validation_error
        )
    try:
        with model_base.get_db() as database:
            candidates = candidatesService(database).get_all_candidates(query_params)
            response_data = {
                "kind": "candidatesListing",
                "field": "name,date_of_birth,submitted_datetime,email,phone,cv_score,job_uuid,status,interview_feedback",
                "items": [candidate.display() for candidate in candidates],
                "page": int(query_params.get("page", 1)),
                "per_page": int(query_params.get("per_page", 10)),
                "total": len(candidates),
            }
            return SuccessResponse(context="/candidates/").generate_response(
                response_data
            )
    except Exception as e:
        print(e)
        return ErrorResponse(context="/candidates/").internal_server_error_response()


@candidates.route("/<candidateId>", methods=["GET"])
def get_a_candidate(candidateId):
    try:
        with model_base.get_db() as db:
            candidate = candidatesService(db).get_candidate_by_id(candidateId)
            if not candidate:
                return ErrorResponse(context="/candidates/").not_found_response()
            else:
                return SuccessResponse(context="/candidates/").generate_response(
                    candidate.display(), 200
                )
    except Exception as e:
        print(e)
        return ErrorResponse(context="/candidates/").internal_server_error_response()


@candidates.route("/", methods=["POST"])
def create_candidate():
    data = request.get_json()
    print(data)
    try:
        candidate = schema_validator.Candidate(**data)
    except ValueError as e:
        return ErrorResponse(context="/candidates/").bad_request_response(str(e))

    try:
        with model_base.get_db() as database:
            created_candidate = candidatesService(database).create_candidate(candidate)

            return SuccessResponse(context="/candidates/").generate_response(
                created_candidate.display(), 201
            )

    except Exception as e:
        logging.error(e)
        return ErrorResponse(context="/candidates/").internal_server_error_response()
