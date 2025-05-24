# API Setup Guide

This guide explains how to obtain all the necessary API keys for running Stocknear's backend.

## Financial Modeling Prep (FMP)
1. Visit [financialmodelingprep.com/developer](https://financialmodelingprep.com/developer)
2. Sign up for an account
3. Choose a plan (free tier available)
4. Find your API key in the dashboard
5. Copy it to your `.env` file as `FMP_API_KEY`

## OpenAI
1. Go to [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key immediately (it won't be shown again)
5. Add it to your `.env` file as `OPENAI_API_KEY`

## CoinGecko
1. Visit [coingecko.com/api/pricing](https://www.coingecko.com/api/pricing)
2. Create an account
3. Select a plan (free tier available)
4. Get your API key from the dashboard
5. Add it to your `.env` file as `COINGECKO_API_KEY`

## Mixpanel
1. Go to [mixpanel.com](https://mixpanel.com/)
2. Create an account
3. Create a new project
4. Navigate to Project Settings > Access Keys
5. Copy your project token
6. Add it to your `.env` file as `MIXPANEL_API_KEY`

## Twitch
1. Visit [dev.twitch.tv/console/apps](https://dev.twitch.tv/console/apps)
2. Log in or create an account
3. Click "Register Your Application"
4. Fill in the required details:
   - Name: Your application name
   - OAuth Redirect URLs: http://localhost:8000 (for development)
   - Category: Choose appropriate category
5. Get both the Client ID and Client Secret
6. Add them to your `.env` file as:
   - Client ID → `TWITCH_API_KEY`
   - Client Secret → `TWITCH_SECRET_KEY`

## Security Notes
- Never commit your `.env` file to version control
- Keep your API keys secure and don't share them
- Be aware of rate limits on free tiers
- Regularly rotate your API keys for better security
- Monitor API usage to avoid unexpected charges 