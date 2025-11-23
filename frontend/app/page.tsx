import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        {/* Header */}
        <header className="text-center mb-16">
          <h1 className="text-5xl md:text-6xl font-bold text-indigo-900 mb-4">
            TBONTB
          </h1>
          <p className="text-xl md:text-2xl text-indigo-800 mb-2">
            To Buy Or Not To Buy
          </p>
          <p className="text-lg text-indigo-700 max-w-2xl mx-auto">
            Make informed financial decisions with advanced Monte Carlo simulations
          </p>
        </header>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="text-4xl mb-4">🏠</div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">Buying Scenario</h3>
            <p className="text-gray-700">
              Simulate apartment purchase with mortgage, property appreciation, and maintenance costs
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="text-4xl mb-4">📈</div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">Investment Scenario</h3>
            <p className="text-gray-700">
              Model direct investment portfolios with fees, taxes, and market volatility
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="text-4xl mb-4">⚖️</div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">Compare Scenarios</h3>
            <p className="text-gray-700">
              Side-by-side comparison with interactive visualizations and probability distributions
            </p>
          </div>
        </div>

        {/* How It Works */}
        <div className="bg-white rounded-lg shadow-lg p-8 mb-16">
          <h2 className="text-3xl font-bold mb-6 text-center text-gray-900">How It Works</h2>
          <div className="grid md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-blue-600">1</span>
              </div>
              <h4 className="font-bold mb-2 text-gray-900">Enter Your Profile</h4>
              <p className="text-sm text-gray-700">Income, savings, and financial goals</p>
            </div>

            <div className="text-center">
              <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-blue-600">2</span>
              </div>
              <h4 className="font-bold mb-2 text-gray-900">Configure Scenarios</h4>
              <p className="text-sm text-gray-700">Apartment price, mortgage, or investment parameters</p>
            </div>

            <div className="text-center">
              <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-blue-600">3</span>
              </div>
              <h4 className="font-bold mb-2 text-gray-900">Run Simulation</h4>
              <p className="text-sm text-gray-700">10,000+ Monte Carlo simulations in seconds</p>
            </div>

            <div className="text-center">
              <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-blue-600">4</span>
              </div>
              <h4 className="font-bold mb-2 text-gray-900">Analyze Results</h4>
              <p className="text-sm text-gray-700">Interactive charts and detailed breakdowns</p>
            </div>
          </div>
        </div>

        {/* CTA */}
        <div className="text-center">
          <Link
            href="/simulate"
            className="inline-block bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 px-8 rounded-lg text-lg transition-colors duration-200 shadow-lg"
          >
            Start Your Simulation
          </Link>
          <p className="mt-4 text-gray-600">
            Free • No registration required • Results in seconds
          </p>
        </div>

        {/* Tech Stack */}
        <div className="mt-16 text-center">
          <p className="text-sm text-gray-500 mb-2">Powered by</p>
          <div className="flex justify-center gap-4 flex-wrap">
            <span className="px-3 py-1 bg-gray-200 rounded text-sm">Monte Carlo Simulation</span>
            <span className="px-3 py-1 bg-gray-200 rounded text-sm">Geometric Brownian Motion</span>
            <span className="px-3 py-1 bg-gray-200 rounded text-sm">Advanced Mortgage Calculator</span>
          </div>
        </div>
      </div>
    </div>
  );
}
