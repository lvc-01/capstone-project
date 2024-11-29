Welcome to our Capstone project

by AWSome-4


Proposed file structure:

|self-storage-app
│
├── /infrastructure          # AWS infrastructure-as-code (e.g., CDK, CloudFormation)
│   ├── /lambda              # Lambda functions (separate per functionality)
│   ├── /api-gateway         # API Gateway configuration (endpoints, methods)
│   ├── /cognito             # Cognito User Pools, Identity Pools, App clients
│   ├── /dynamodb            # DynamoDB Tables (Bookings, Users, Units)
│   ├── /ses                 # SES Email Templates & Email Configuration
│   ├── /s3                  # S3 Bucket for Static Website Hosting
│   ├── /cloudfront          # CloudFront Distribution Setup
│   ├── /eventbridge         # EventBridge rules for event-driven processes
│   ├── /sqs                 # SQS Queues for background tasks
│   └── /cloudformation.yml  # CloudFormation Template (or CDK/ SAM)
│
├── /backend                 # AWS Lambda functions
│   ├── /bookUnit            # Lambda function for booking units
│   ├── /cancelUnit          # Lambda function for canceling bookings
│   ├── /unlockUnit          # Lambda function for unlocking units
│   ├── /statusUnit          # Lambda function for checking unit status
│   ├── /sendNotification    # Lambda function for sending email notifications
│   ├── /processInvoice      # Lambda function for invoice processing
│   └── /utils               # Common utility functions (e.g., helper functions)
│
├── /frontend                # Frontend code for static website
│   ├── /assets              # Static assets (images, CSS, JavaScript)
│   ├── /components          # React/Vue components (or plain HTML templates)
│   ├── /pages               # Web pages (Booking page, Login page, etc.)
│   ├── /services            # API call services to interact with backend
│   ├── /utils               # Helper functions for frontend logic
│   └── /index.html          # Entry point for the website
│
├── /tests                   # Unit & Integration tests
│   ├── /backend             # Backend tests for Lambda functions
│   ├── /frontend            # Frontend tests (React, Cypress, etc.)
│   ├── /integration         # Integration tests for API Gateway and Lambda
│   └── /utils               # Helper tests for utilities and shared code
│
├── /scripts                 # Helper scripts for automation (CI/CD, deployments, etc.)
│   ├── /deploy.sh           # Deploy project via CloudFormation/CDK
│   ├── /build.sh            # Build frontend assets
│   ├── /setup.sh            # Setup scripts (e.g., Cognito, DynamoDB)
│   └── /test.sh             # Run tests locally or in CI
│
├── /config                  # Configuration files for the project
│   ├── /cognito-config.json # Cognito User Pool configurations
│   ├── /dynamodb-config.json# DynamoDB table schema definitions
│   ├── /api-config.json     # API Gateway endpoint settings
│   ├── /email-config.json   # SES email templates and settings
│   └── /app-config.json     # Application specific configurations (URLs, settings)
│
└── README.md                # Project README (overview, setup instructions)
