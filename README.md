# NxtBn's SSLCommerz Payment Link Plugin


## Installation

### Via NxtBn Dashboard
1. Go to the Plugins section in the dashboard: Plugins > Upload Plugin.
2. During the upload, select the plugin category as "payment_processor".

### Manually
1. Download or clone this project.
2. Place the files in your NxtBn codebase at this location: nxtbn/payment/plugin/.

That's it! The plugin will automatically be recognized by the system.


# Configuration
The SSLCOmmerz Payment Link Plugin requires the following environment variables to be set:

- `SSLCOMMERZ_STORE_ID=`
- `SSLCOMMERZ_STORE_PASSWORD=`

- `SSLCOMMERZ_INIT_URL=`
- `SSLCOMMERZ_VALIDATE_URL=`
`SSLCOMMERZ_SANDBOX=`

- `SSLCommerz_SUCCESS_URL= `
- `SSLCommerz_CANCEL_URL=`
- `SSLCommerz_FAIL_URL=`

### Updating .env Variables
You can update these variables either via the NxtBn dashboard under `Settings` > `.env` button or directly in the terminal using:
```bash
nano .env
```

#

# SSLCommerz Integration Guide

## Step 1: Register for an SSLCommerz Developer Account

1. **Visit the SSLCommerz Website**
   - Go to the [SSLCommerz registration page](https://developer.sslcommerz.com/registration/).

2. **Fill Out the Registration Form**
   - Provide the necessary details such as your name, email, phone number, company name, and other required information.
   - Ensure to select the option for a **developer account** if available, or mention that you are looking for a developer/sandbox account in the description field.

3. **Submit the Form**
   - Submit the form and wait for an email from SSLCommerz. They will send you further instructions or approval information.

## Step 2: Configure Your Account

1. **Login to Your Account**
   - After receiving approval, log in to your SSLCommerz account.

2. **Access API Credentials**
   - Navigate to the **API** section or **Integration** section in your account dashboard. Here, you should find your **Store ID** and **Store Password**.

3. **Take Note of Important URLs**
   - SSLCommerz provides several URLs for initiating and validating transactions, as well as for handling success, failure, and cancellation responses. These URLs are generally documented in their API documentation. Below are the typical URLs you will use:

   - `SSLCOMMERZ_INIT_URL`: URL to initiate a transaction.
   - `SSLCOMMERZ_VALIDATE_URL`: URL to validate a transaction.

4. **Set Up Return URLs**
   - You will need to configure the URLs to which SSLCommerz will redirect users after a transaction. These are:
     - `SSLCommerz_SUCCESS_URL`: URL to redirect on successful payment.
     - `SSLCommerz_CANCEL_URL`: URL to redirect if the payment is canceled.
     - `SSLCommerz_FAIL_URL`: URL to redirect on failed payment.

5. **Enable Sandbox Mode (if applicable)**
   - If you are working in a development environment, you might need to use the sandbox mode. The sandbox URLs and environment setup will be provided in the documentation or your account settings. Set the `SSLCOMMERZ_SANDBOX` value to `true` or `false` based on your environment.

## Example Configuration

Here is an example of how these values might look in a configuration file or environment variables:

```env
SSLCOMMERZ_STORE_ID=your_store_id
SSLCOMMERZ_STORE_PASSWORD=your_store_password
SSLCOMMERZ_INIT_URL=https://sandbox.sslcommerz.com/gwprocess/v4/api.php
SSLCOMMERZ_VALIDATE_URL=https://sandbox.sslcommerz.com/validator/api/validationserverAPI.php
SSLCOMMERZ_SANDBOX=true
SSLCommerz_SUCCESS_URL=https://yourwebsite.com/payment/success
SSLCommerz_CANCEL_URL=https://yourwebsite.com/payment/cancel
SSLCommerz_FAIL_URL=https://yourwebsite.com/payment/fail
```