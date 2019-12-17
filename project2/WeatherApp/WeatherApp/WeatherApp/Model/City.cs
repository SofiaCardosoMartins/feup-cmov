﻿using System;
using WeatherApp.ViewModel;

namespace WeatherApp.Model
{
    public class City
    {
        private string Name;

        private Weather CurrentWeather;

        private Forecast LastForecast;

        private CityViewModel Proxy;

        public City(string n, CityViewModel vm)
        {
            Name = n;
            Proxy = vm;
        }

        public void UpdateWeather(Weather weather)
        {
            CurrentWeather = weather;
            Proxy.UpdateViewModel(this);
        }

        public void UpdateForecast(Forecast forecast)
        {
            LastForecast = forecast;
            Proxy.UpdateViewModel(this);
        }

        public string getName()
        {
            return Name;
        }

        public Weather getWeather()
        {
            return CurrentWeather;
        }

        public Forecast GetForecast()
        {
            return LastForecast;
        }

    }
}
