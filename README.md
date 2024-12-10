# Digital Self-Storage Solution

A modern, serverless self-storage management system built on AWS, enabling customers to rent, manage, and access storage units through a web application without human intervention.

## Features

### Storage Management
- Browse available storage units across different facilities
- View unit sizes and pricing
- Real-time availability checking
- Instant booking capabilities
- Flexible rental periods (1 day to indefinite)

### Security
- Secure authentication via AWS Cognito
- Digital access control for storage units
- Access sharing with time-based permissions
- Real-time notifications for unit access
- Comprehensive access logging

### Payment & Billing
- Multiple payment methods (Card, EFT)
- Flexible billing options (Pre-pay, Monthly, Yearly)
- Dynamic discount system
- Automated invoice generation
- Secure payment processing

### Customer Features
- Self-service booking management
- Digital access control via web app
- Payment method management
- Access sharing capabilities
- Custom notifications

## Technical Architecture

### Backend Services
- **API Gateway**: RESTful API endpoints
- **AWS Lambda**: Serverless business logic
- **DynamoDB**: NoSQL data storage
- **Cognito**: User authentication
- **SQS & EventBridge**: Asynchronous event handling
- **SES**: Email notifications
- **S3 & CloudFront**: Static web hosting

### Frontend
- React-based web application
- Responsive design
- AWS Amplify integration
- Real-time updates

## Getting Started

### Prerequisites
- AWS Account with appropriate permissions
- Node.js (v14 or later)
- AWS CLI configured
- Python 3.8+ (for Lambda functions)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/your-org/self-storage-solution.git
cd self-storage-solution
```

2. Install dependencies:
```bash
npm install
```

3. Deploy the backend infrastructure:
```bash
npm run deploy:backend
```

4. Deploy the frontend application:
```bash
npm run deploy:frontend
```

### Configuration

1. Create a `.env` file in the project root:
```
AWS_REGION=your-region
COGNITO_USER_POOL_ID=your-user-pool-id
COGNITO_CLIENT_ID=your-client-id
API_ENDPOINT=your-api-endpoint
```

2. Configure AWS services:
- Set up Cognito User Pool
- Configure SES for email notifications
- Set up required IAM roles and policies

## Development

### Project Structure
```
/
├── backend/
│   ├── functions/          # Lambda functions
│   ├── lib/               # Shared utilities
│   └── resources/         # CloudFormation templates
├── frontend/
│   ├── src/              # React application source
│   ├── public/           # Static assets
│   └── config/           # Frontend configuration
└── infrastructure/       # IaC templates
```

### Running Locally

1. Start the frontend development server:
```bash
cd frontend
npm run start
```

2. Deploy backend changes:
```bash
cd backend
npm run deploy
```

### Testing

Run the test suite:
```bash
npm run test
```

Run integration tests:
```bash
npm run test:integration
```

## Deployment

### Backend Deployment
The backend is deployed using CloudFormation:
1. Package the application:
```bash
npm run package
```

2. Deploy to AWS:
```bash
npm run deploy
```

### Frontend Deployment
The frontend is deployed to S3 and distributed via CloudFront:
```bash
npm run deploy:frontend
```

## API Documentation

API documentation is available at:
- Development: `https://api-dev.your-domain.com/docs`
- Production: `https://api.your-domain.com/docs`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Security

For security concerns, please contact security@your-domain.com

## License

This project is licensed under the MIT License - see the LICENSE file for details

## Support

For support, email support@your-domain.com or create an issue in the repository.
