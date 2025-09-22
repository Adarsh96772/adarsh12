import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Shield, Mail, Lock, Eye, EyeOff, LogIn, Smartphone } from 'lucide-react';
import { authAPI } from '../services/api';
import authService from '../services/authService';
import toast from 'react-hot-toast';

const LoginPage = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [errors, setErrors] = useState({ email: '', password: '' });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [role, setRole] = useState('user'); // 'user' | 'police'
  const [policeAccessCode, setPoliceAccessCode] = useState('');
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    // Clear field error on change
    if (errors[e.target.name]) {
      setErrors({ ...errors, [e.target.name]: '' });
    }
  };

  const handleBlur = (e) => {
    const { name, value } = e.target;
    if (name === 'email') {
      if (!value) {
        setErrors((prev) => ({ ...prev, email: 'Email is required' }));
      } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
        setErrors((prev) => ({ ...prev, email: 'Enter a valid email address' }));
      }
    }
    if (name === 'password') {
      if (!value) {
        setErrors((prev) => ({ ...prev, password: 'Password is required' }));
      } else if (value.length < 6) {
        setErrors((prev) => ({ ...prev, password: 'Password must be at least 6 characters' }));
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Final validation before submit
    const nextErrors = { email: '', password: '' };
    if (!formData.email) nextErrors.email = 'Email is required';
    if (!formData.password) nextErrors.password = 'Password is required';
    if (formData.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      nextErrors.email = 'Enter a valid email address';
    }
    if (formData.password && formData.password.length < 6) {
      nextErrors.password = 'Password must be at least 6 characters';
    }
    // Additional validation for Police role
    if (role === 'police') {
      const requiredCode = process.env.REACT_APP_POLICE_CODE || 'POLICE-2025';
      const looksPoliceEmail = /gov$|police/i.test(formData.email);
      if (!policeAccessCode) {
        toast.error('Police access code is required');
        return;
      }
      if (policeAccessCode !== requiredCode) {
        toast.error('Invalid police access code');
        return;
      }
      if (!looksPoliceEmail) {
        toast('Hint: use your department email (e.g., name@city.police.gov)', { icon: 'ℹ️' });
      }
    }
    if (nextErrors.email || nextErrors.password) {
      setErrors(nextErrors);
      toast.error('Please fix the highlighted fields');
      return;
    }

    setLoading(true);
    try {
      const response = await authAPI.login(formData);
      const { token, tourist } = response.data;

      authService.setAuth(token, tourist);
      authService.setRole(role);
      toast.success(`Welcome back, ${tourist.name}!`);

      // Dispatch auth state change event
      window.dispatchEvent(new Event('authStateChanged'));

      navigate(role === 'police' ? '/police-dashboard' : '/dashboard');
    } catch (error) {
      console.error('Login failed:', error);
      const status = error.response?.status;
      const backendMsg = error.response?.data?.message;
      let errorMessage = 'Invalid email or password. Please try again.';

      if (!error.response) {
        errorMessage = 'Network error. Please check your connection and try again.';
      } else if (status === 404) {
        errorMessage = 'No account found for this email. Please sign up.';
      } else if (status === 401) {
        errorMessage = 'Invalid password. Please try again.';
      } else if (status === 400) {
        errorMessage = backendMsg || 'Password not set for this user. Please reset your password or contact support.';
      } else if (backendMsg) {
        errorMessage = backendMsg;
      }

      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-600 via-indigo-700 to-purple-800 py-12 px-4 sm:px-6 lg:px-8 dark:from-gray-900 dark:via-gray-900 dark:to-gray-900">
      <div className="max-w-md w-full space-y-8 bg-white dark:bg-gray-900 rounded-2xl shadow-2xl p-8 backdrop-blur-sm bg-opacity-95 dark:bg-opacity-95">
        {/* Header */}
        <div className="text-center">
          <div className="mx-auto h-24 w-24 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mb-6 shadow-xl transform hover:scale-105 transition-transform border-4 border-white">
            <Shield className="h-12 w-12 text-white" />
          </div>
          <h2 className="text-4xl font-extrabold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Welcome Back
          </h2>
          <p className="mt-3 text-base text-gray-600 dark:text-gray-300">
            Sign in to your Smart Tourist Safety account
          </p>
        </div>

        {/* Login Form */}
        <form className="mt-8 space-y-6" onSubmit={handleSubmit} noValidate>
          {/* Role Selector */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Sign in as</label>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => setRole('user')}
                className={`w-full px-3 py-2 rounded-lg border text-sm font-medium transition-all
                  ${role === 'user' 
                    ? 'bg-blue-600 text-white border-blue-600 shadow' 
                    : 'bg-white text-gray-700 border-gray-300 hover:border-blue-300'}
                `}
                aria-pressed={role === 'user'}
              >
                Tourist User
              </button>
              <button
                type="button"
                onClick={() => setRole('police')}
                className={`w-full px-3 py-2 rounded-lg border text-sm font-medium transition-all
                  ${role === 'police' 
                    ? 'bg-indigo-600 text-white border-indigo-600 shadow' 
                    : 'bg-white text-gray-700 border-gray-300 hover:border-indigo-300'}
                `}
                aria-pressed={role === 'police'}
              >
                Police Officer
              </button>
            </div>
          </div>
          <div className="space-y-5">
            {/* Email Input */}
            <div>
              <label htmlFor="email" className="block text-sm font-semibold text-gray-700 mb-2">
                Email Address
              </label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail className="h-5 w-5 text-blue-500 group-hover:text-blue-600 transition-colors" />
                </div>
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  value={formData.email}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  aria-invalid={!!errors.email}
                  aria-describedby="email-error"
                  className={`block w-full pl-10 pr-3 py-3.5 border-2 rounded-xl shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 transition-all hover:border-blue-300 
                    ${errors.email ? 'border-red-400 focus:ring-red-500 focus:border-red-500' : 'border-gray-200 focus:ring-blue-500 focus:border-blue-500'}`}
                  placeholder="Enter your email"
                />
                {errors.email && (
                  <p id="email-error" className="mt-2 text-sm text-red-600">{errors.email}</p>
                )}
              </div>
            </div>

            {/* Password Input */}
            <div>
              <label htmlFor="password" className="block text-sm font-semibold text-gray-700 mb-2">
                Password
              </label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-blue-500 group-hover:text-blue-600 transition-colors" />
                </div>
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  value={formData.password}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  aria-invalid={!!errors.password}
                  aria-describedby="password-error"
                  className={`block w-full pl-10 pr-12 py-3.5 border-2 rounded-xl shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 transition-all hover:border-blue-300 
                    ${errors.password ? 'border-red-400 focus:ring-red-500 focus:border-red-500' : 'border-gray-200 focus:ring-blue-500 focus:border-blue-500'}`}
                  placeholder="Enter your password"
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5 text-blue-500 hover:text-blue-700" />
                  ) : (
                    <Eye className="h-5 w-5 text-blue-500 hover:text-blue-700" />
                  )}
                </button>
                {errors.password && (
                  <p id="password-error" className="mt-2 text-sm text-red-600">{errors.password}</p>
                )}
              </div>
            </div>
          </div>

          {/* Remember Me & Forgot Password */}
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <input
                id="remember-me"
                name="remember-me"
                type="checkbox"
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-700">
                Remember me
              </label>
            </div>
            <button
              type="button"
              className="text-sm text-blue-600 hover:text-blue-500 font-medium"
            >
              Forgot password?
            </button>
          </div>

          {/* Police Access Code (only when role is police) */}
          {role === 'police' && (
            <div className="mt-3">
              <label htmlFor="policeCode" className="block text-sm font-semibold text-gray-700 mb-2">
                Police Access Code
              </label>
              <input
                id="policeCode"
                name="policeCode"
                type="text"
                value={policeAccessCode}
                onChange={(e) => setPoliceAccessCode(e.target.value)}
                placeholder="Enter department access code"
                className="block w-full px-3 py-3.5 border-2 border-gray-200 rounded-xl shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all"
              />
              <p className="mt-1 text-xs text-gray-500">Use your department-issued code. Contact admin if you don’t have one.</p>
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transform transition-all duration-200 hover:scale-105 shadow-lg"
          >
            {loading ? (
              <div className="flex items-center">
                <svg className="animate-spin h-5 w-5 mr-2 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path>
                </svg>
                Signing in...
              </div>
            ) : (
              <div className="flex items-center">
                <LogIn className="h-5 w-5 mr-2" />
                Sign In
              </div>
            )}
          </button>

          {/* Demo Autofill */}
          <button
            type="button"
            onClick={() => setFormData({ email: 'demo@tourist.com', password: 'demo123' })}
            className="group relative w-full flex justify-center py-2.5 px-4 border-2 border-blue-200 text-sm font-medium rounded-lg text-blue-700 bg-white hover:bg-blue-50 hover:border-blue-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transform transition-all duration-200"
          >
            Autofill Demo Credentials
          </button>

          {/* Divider */}
          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white dark:bg-gray-900 text-gray-500">Don't have an account?</span>
            </div>
          </div>

          {/* Sign Up Link */}
          <Link
            to="/register"
            className="group relative w-full flex justify-center py-3 px-4 border-2 border-gray-300 text-sm font-medium rounded-lg text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-900 hover:bg-gray-50 dark:hover:bg-gray-800 hover:border-blue-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transform transition-all duration-200 hover:scale-105"
          >
            <Smartphone className="h-5 w-5 mr-2 text-blue-500" />
            Create New Account
          </Link>
        </form>

        {/* Quick Demo Info */}
        <div className="mt-8 p-5 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-gray-800 dark:to-gray-800 rounded-xl border border-blue-200 dark:border-gray-700 shadow-sm hover:shadow-md transition-all duration-300">
          <div className="text-center">
            <Shield className="h-8 w-8 text-blue-500 mx-auto mb-3 animate-pulse" />
            <h4 className="text-base font-bold text-blue-700 mb-2">Demo Account</h4>
            <div className="bg-white p-3 rounded-lg border border-blue-100 inline-block">
              <p className="text-sm text-blue-600 font-medium">
                Email: <span className="font-mono">demo@tourist.com</span><br />
                Password: <span className="font-mono">demo123</span>
              </p>
            </div>
          </div>
        </div>

        {/* Features */}
        <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-3">
          {[
            { icon: Shield, title: 'Secure', desc: 'End-to-end encryption' },
            { icon: Smartphone, title: 'Mobile First', desc: 'Optimized for mobile' },
            { icon: LogIn, title: 'Quick Access', desc: 'Fast authentication' }
          ].map((feature, index) => {
            const Icon = feature.icon;
            return (
              <div key={index} className="text-center">
                <div className="w-8 h-8 bg-gradient-to-r from-blue-100 to-purple-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                  <Icon className="h-4 w-4 text-blue-600" />
                </div>
                <h4 className="text-xs font-medium text-gray-700">{feature.title}</h4>
                <p className="text-xs text-gray-500">{feature.desc}</p>
              </div>
            );
          })}
        </div>

        {/* Footer */}
        <div className="text-center text-xs text-gray-500 dark:text-gray-400 mt-8">
          <p>
            By signing in, you agree to our{' '}
            <button className="text-blue-600 hover:underline">Terms of Service</button>
            {' '}and{' '}
            <button className="text-blue-600 hover:underline">Privacy Policy</button>
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;