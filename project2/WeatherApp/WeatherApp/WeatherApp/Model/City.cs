﻿using System;
using System.Collections.Generic;
using WeatherApp.ViewModel;
using Xamarin.Forms;

namespace WeatherApp.Model
{
    public class ForecastPair
    {
        public string Hour { get; set; }
        public MainStats Stats { get; set; }

        public ForecastPair(string h, MainStats s)
        {
            Hour = h;
            Stats = s;
        }
    }

    public class Gradient
    {
        public string First { get; set; }
        public string Second { get; set; }

        public Gradient(string f, string s)
        {
            First = f;
            Second = s;
        }
    }

    public class City : DynamicViewModel
    {
        public static readonly int NUM_SELECTED_FORECASTS = 8;
        public static readonly int HOURS_MINS_STRING_SIZE = 5;

        public string Name { get; set; }

        private string _Description;
        public string Description { get => _Description; set => SetProperty(ref _Description, value); }

        private string _CurrentTemp = "--ºC";
        public string CurrentTemp { get => _CurrentTemp; set => SetProperty(ref _CurrentTemp, value); }

        public MainStats _CurrentStats;
        public MainStats CurrentStats { get => _CurrentStats; set => SetProperty(ref _CurrentStats, value); }

        public List<ForecastPair> _HourlyStats;
        public List<ForecastPair> HourlyStats { get => _HourlyStats; set => SetProperty(ref _HourlyStats, value); }

        public string[] _Hours = { "--" };
        public string[] Hours { get => _Hours; set => SetProperty(ref _Hours, value); }

        public float[] _Temps = { 0 };
        public float[] Temps { get => _Temps; set => SetProperty(ref _Temps, value); }

        public float[] _Precipitations = { 0 };
        public float[] Precipitations { get => _Precipitations; set => SetProperty(ref _Precipitations, value); }

        public ImageSource[] _Icons = { };
        public ImageSource[] Icons { get => _Icons; set => SetProperty(ref _Icons, value); }

        
        public Gradient Grad { get; set; } //"#a0dedb", "#03a4d1");

        public void UpdateModel(Weather weather)
        {
            Description = weather.weather[0].description;
            CurrentTemp = Math.Round(weather.main.temp, 1).ToString() + "ºC";
            CurrentStats = new MainStats(weather);
        }

        public void DetailedUpdateModel(Forecast forecast)
        {
            List<ForecastPair> TempHourlyStats = new List<ForecastPair>();
            string[] TempHours = new string[NUM_SELECTED_FORECASTS];
            float[] TempTemps = new float[NUM_SELECTED_FORECASTS];
            float[] TempPrecipitations = new float[NUM_SELECTED_FORECASTS];
            ImageSource[] TempIcons = new ImageSource[NUM_SELECTED_FORECASTS];

            for (int i = 0; i < forecast.list.Count && i < NUM_SELECTED_FORECASTS; ++i)
            {
                Entry temp = forecast.list[i];
                string time = temp.dt_txt.Split(' ')[1].Remove(HOURS_MINS_STRING_SIZE);
                MainStats stats = new MainStats(temp);

                TempHourlyStats.Add(new ForecastPair(time, stats));
                TempHours.SetValue(time + "h", i);
                TempTemps.SetValue((float) Math.Round(temp.main.temp, 1), i);
                TempPrecipitations.SetValue((float)Math.Round(temp.rain != null ? temp.rain["3h"] : 0, 1), i);
                TempIcons.SetValue(stats.Icon, i);
            }

            // Setting with properties with final values
            HourlyStats = TempHourlyStats;
            Hours = TempHours;
            Temps = TempTemps;
            Precipitations = TempPrecipitations;
            Icons = TempIcons;
        }
    }
}
