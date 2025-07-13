# LME Dashboard

A comprehensive web dashboard for tracking London Metal Exchange (LME) metal prices, market trends, and analytics.

## Overview

This dashboard provides real-time and historical data visualization for LME metal commodities including copper, aluminum, zinc, lead, nickel, and tin. Built for traders, analysts, and industry professionals to monitor market movements and make informed decisions.

## Features

- **Real-time Price Tracking**: Live updates of LME metal prices
- **Historical Data Analysis**: Charts and graphs showing price trends over time
- **Market Analytics**: Technical indicators and market insights
- **Portfolio Tracking**: Monitor your metal commodity investments
- **Price Alerts**: Customizable notifications for price movements
- **Export Functionality**: Download data in various formats (CSV, Excel, PDF)
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices

## Tech Stack

- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Charts**: Chart.js / D3.js
- **API**: LME official data feeds
- **Styling**: CSS Grid/Flexbox, responsive design
- **Build Tools**: Modern JavaScript bundling

## Getting Started

### Prerequisites

- Node.js (v14 or higher)
- npm or yarn package manager
- Modern web browser

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/lme-dashboard.git
cd lme-dashboard
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

4. Start the development server:
```bash
npm start
```

5. Open your browser to `http://localhost:3000`

## Configuration

### API Setup

1. Obtain LME data API credentials
2. Configure API endpoints in `config/api.js`
3. Set refresh intervals and data sources

### Customization

- Modify `src/config/metals.js` to add/remove tracked metals
- Adjust chart settings in `src/components/charts/`
- Update styling in `src/styles/`

## Usage

### Dashboard Navigation

- **Overview**: Main dashboard with key metrics
- **Live Prices**: Real-time price feeds
- **Charts**: Historical price charts and technical analysis
- **Alerts**: Configure price movement notifications
- **Reports**: Generate and export market reports

### Setting Up Alerts

1. Navigate to the Alerts section
2. Select metal commodity
3. Set price threshold and alert type
4. Choose notification method (email, browser, SMS)

## API Documentation

### Endpoints

- `GET /api/prices/live` - Real-time prices
- `GET /api/prices/historical` - Historical data
- `GET /api/metals` - Available metals list
- `POST /api/alerts` - Create price alert

### Data Format

```json
{
  "metal": "copper",
  "price": 8245.50,
  "currency": "USD",
  "unit": "per tonne",
  "timestamp": "2024-07-13T10:30:00Z",
  "change": "+1.2%"
}
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## Testing

```bash
# Run unit tests
npm test

# Run integration tests
npm run test:integration

# Run all tests with coverage
npm run test:coverage
```

## Deployment

### Production Build

```bash
npm run build
```

### Docker Deployment

```bash
docker build -t lme-dashboard .
docker run -p 3000:3000 lme-dashboard
```

## Security

- API keys are stored securely in environment variables
- All data transmission uses HTTPS
- Input validation and sanitization implemented
- Regular security updates for dependencies

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- Create an issue for bug reports or feature requests
- Email: support@lmedashboard.com
- Documentation: [Wiki](https://github.com/yourusername/lme-dashboard/wiki)

## Acknowledgments

- London Metal Exchange for data access
- Chart.js community for visualization tools
- Contributors and maintainers

## Roadmap

- [ ] Mobile app development
- [ ] Advanced analytics and ML predictions
- [ ] Multi-language support
- [ ] Dark mode theme
- [ ] Integration with trading platforms
- [ ] Real-time news feed integration

---

**Disclaimer**: This dashboard is for informational purposes only. Always verify data with official LME sources before making trading decisions.