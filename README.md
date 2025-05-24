<div align="center">



# **Stocknear: Open Source Stock Analysis Platform**

<h3>

[Homepage](https://stocknear.com/) | [Discord](https://discord.com/invite/hCwZMMZ2MT)

</h3>

[![GitHub Repo stars](https://img.shields.io/github/stars/stocknear/backend)](https://github.com/stocknear/backend/stargazers)

</div>



# Techstack

This is the codebase that powers [stocknear's](https://stocknear.com/) backend, which is an open-source stock analysis research platform.

Built with:
- [FastAPI](https://fastapi.tiangolo.com/): Python Backend
- [Fastify](https://fastify.dev/): Nodejs Backend
- [Pocketbase](https://pocketbase.io/): Database
- [Redis](https://redis.io/): Caching Data

# Environment Setup

To run the backend, you'll need to set up environment variables in a `.env` file. Required API keys:

- FMP API Key ([Financial Modeling Prep](https://financialmodelingprep.com/developer))
- OpenAI API Key ([OpenAI Platform](https://platform.openai.com/api-keys))
- CoinGecko API Key ([CoinGecko](https://www.coingecko.com/api/pricing))
- Mixpanel API Key ([Mixpanel](https://mixpanel.com/))
- Twitch API Keys ([Twitch Dev Console](https://dev.twitch.tv/console/apps))

For detailed instructions on obtaining these API keys, see our [API Setup Guide](docs/API_SETUP.md).

## Project Structure and Environment Configuration

The backend consists of two main services: a FastAPI application (in the `app` directory) and a Fastify server (in the `fastify` directory). The environment variables need to be configured for the FastAPI service.

Below is the basic structure of the backend repository:

```
backend/
├── app/
│   ├── Dockerfile
│   ├── .env           <- Place your .env file here
│   └── ...
├── fastify/
│   ├── Dockerfile
│   └── ...
└── docker-compose.yml
```

Create a `.env` file in the `app` directory with this template:
```env
# Financial Modeling Prep API Key
FMP_API_KEY=your_fmp_key_here

# OpenAI API Key
OPENAI_API_KEY=your_openai_key_here

# CoinGecko API Key
COINGECKO_API_KEY=your_coingecko_key_here

# Mixpanel API Key
MIXPANEL_API_KEY=your_mixpanel_key_here

# Twitch API Keys
TWITCH_API_KEY=your_twitch_key_here
TWITCH_SECRET_KEY=your_twitch_secret_here
```

## Running the Backend

Once you have set up your environment file, you can start the backend services using Docker Compose:

```bash
docker compose -f frontend/docker-compose.yml up --build -d
```

Note: The `.env` file is ignored by git for security reasons. Never commit your API keys to version control.

# Contributing
Stocknear is an open-source project, soley maintained by Muslem Rahimi.

We are not accepting pull requests. However, you are more than welcome to fork the project and customize it to suit your needs.

The core idea of stocknear shall always be: **_Fast_**, **_Simple_** & **_Efficient_**.


# Support ❤️

If you love the idea of stocknear and want to support our mission you can help us in two ways:

- Become a [Pro Member](https://stocknear.com/pricing) of stocknear to get unlimited feature access to enjoy the platform to the fullest.
- You can sponsor us via [Github](https://github.com/sponsors/stocknear) to help us pay the servers & data providers to keep everything running!
