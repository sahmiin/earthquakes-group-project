#!/usr/bin/env bash
source .env

TERRAFORM_DIR="./terraform"
PIPELINE_DIR="./pipeline"
DASHBOARD_DIR="./dashboard"
DATABASE_DIR="./database"
APP_DIR="./app"
ALERTS_DIR="./alerts"
REPORT_DIR="./weekly_report"

log() {
    echo -e "\n🌋 $1\n"
}


log "Starting full infrastructure and deployment run..."


log "Running terraform init..."
cd "$TERRAFORM_DIR"
terraform init


log "Applying ECR repositories only..."
terraform apply -auto-approve \
    -target='aws_ecr_repository.repositories["pipeline"]' \
    -target='aws_ecr_repository.repositories["dashboard"]' \
    -target='aws_ecr_repository.repositories["archive"]'
cd ..


log "Building & pushing pipeline image..."
cd "$PIPELINE_DIR"
sh ./dockerise.sh
cd ..


log "Building & pushing dashboard image..."
cd "$DASHBOARD_DIR"
sh ./dockerise.sh
cd ..


log "Building & pushing API image..."
cd "$APP_DIR"
sh ./dockerise.sh
cd ..


log "Building & pushing alerts image..."
cd "$ALERTS_DIR"
sh ./dockerise.sh
cd ..


log "Building & pushing weekly report image..."
cd "$REPORT_DIR"
sh ./dockerise.sh
cd ..


log "Applying remaining resources..."
cd "$TERRAFORM_DIR"
terraform apply -auto-approve


log "Running database creation & seed..."
cd "$DATABASE_DIR"
./run_db.sh
cd ..


log "🌏 All done! Infrastructure and images are fully deployed."