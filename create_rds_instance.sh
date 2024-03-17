#!/bin/bash

# Define RDS instance parameters
DB_INSTANCE_IDENTIFIER="mydbinstance"
DB_INSTANCE_CLASS="db.t2.micro"
ENGINE="postgres"
ENGINE_VERSION="12.4"
MASTER_USERNAME="udemyuser"
MASTER_PASSWORD="mypassword123"
DB_NAME="financial_data"
ALLOCATED_STORAGE=20
SUBNET_GROUP_NAME="mydb-subnet-group"
SUBNETS="subnet-<your-id>,subnet-<your-id>"

# Create DB Subnet Group
aws rds create-db-subnet-group \
    --db-subnet-group-name $SUBNET_GROUP_NAME \
    --db-subnet-group-description "Subnet group for my RDS DB Instance" \
    --subnet-ids $SUBNETS

# Create RDS instance
aws rds create-db-instance \
    --db-instance-identifier $DB_INSTANCE_IDENTIFIER \
    --db-instance-class $DB_INSTANCE_CLASS \
    --engine $ENGINE \
    --engine-version $ENGINE_VERSION \
    --master-username $MASTER_USERNAME \
    --master-user-password $MASTER_PASSWORD \
    --allocated-storage $ALLOCATED_STORAGE \
    --db-name $DB_NAME \
    --db-subnet-group-name $SUBNET_GROUP_NAME \
    --no-publicly-accessible
