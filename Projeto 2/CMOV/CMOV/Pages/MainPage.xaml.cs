using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Xamarin.Forms;
using SkiaSharp;
using SkiaSharp.Views.Forms;
using CMOV.Logic;
using CMOV.Models;
using System.Threading;

namespace CMOV
{
    public partial class MainPage : ContentPage
    {
        //App's available Companies 
        List<SelectableData<Company>> companiesDataList;

        //Stocks
        StockObject stock1;
        StockObject stock2;

        bool extended = false;
        bool doubleGraphScale = false;


        public MainPage()
        {
            InitializeComponent();

            NavigationPage.SetHasNavigationBar(this, false);
            LoadCompaniesListView();

            Timer t = new Timer(UIUpdate, null, 1000, 1000); //Checks and Updates UI every 1 second
        }

        #region Graph Rendering
        //Load Stocks asynchronously and request request graph to be painted
        private async void ReloadStocks()
        {
            List<Company> selectedCompanies = GetSelectedCompaniesList();
            switch (selectedCompanies.Count)
            {
                case 1:
                    stock1 = await StocksHandler.GetStockDataAsync(selectedCompanies[0].ticker);
                    stock2 = null;
                    doubleGraphScale = false;
                    break;
                case 2:
                    stock1 = await StocksHandler.GetStockDataAsync(selectedCompanies[0].ticker);
                    stock2 = await StocksHandler.GetStockDataAsync(selectedCompanies[1].ticker);
                    break;
                default:
                    stock1 = null;
                    stock2 = null;
                    doubleGraphScale = false;
                    break;
            }

            Device.BeginInvokeOnMainThread(() =>
            {
                canvasView.InvalidateSurface();
            });
        }

        //Paints graph
        private void CanvasViewPaintSurface(object sender, SKPaintSurfaceEventArgs e)
        {
            CanvasHandler.CanvasDraw(e, stock1, stock2, extended, doubleGraphScale);
        }

        //Handle tapping in the graph event
        void OnCanvasViewTapped(object sender, EventArgs args)
        {
            doubleGraphScale ^= true;
            (sender as SKCanvasView).InvalidateSurface();
        }

        void OnCanvasViewRightSwiped(object sender, EventArgs args)
        {
            extended = true;
            (sender as SKCanvasView).InvalidateSurface();
        }

        void OnCanvasViewLeftSwiped(object sender, EventArgs args)
        {
            extended = false;
            (sender as SKCanvasView).InvalidateSurface();
        }

        #endregion



        #region General Actions
        //Handles Switch toogle event
        private void Switch_Toggled(Object sender, EventArgs e)
        {
            List<Company> selectedCompanies = GetSelectedCompaniesList();
            if (selectedCompanies.Count > 2)
            {
                DisplayAlert("Too many selections", "You can't selected more than 2 companies at a time", "Ok");
                (sender as Switch).IsToggled = false;
                return;
            }

            ReloadStocks();
        }

        //Checks and Updates UI
        public void UIUpdate(object state)
        {
            List<Company> selectedCompanies = GetSelectedCompaniesList();

            //If for some reason selections doesnt match with stocks, update
            if ((selectedCompanies.Count == 0) && (stock1 != null || stock2 != null))
                ReloadStocks();
            else if ((selectedCompanies.Count == 1) && (stock1 == null || stock2 != null))
                ReloadStocks();
            else if ((selectedCompanies.Count == 2) && (stock1 == null || stock2 == null))
                ReloadStocks();
        }
        #endregion



        #region Companies List
        //Load Companies List
        private void LoadCompaniesListView()
        {
            companiesDataList = new List<SelectableData<Company>>
            {
                new SelectableData<Company>(new Company("Advanced Micro Devices, Inc.", "AMD", "Images/AMD.png")),
                new SelectableData<Company>(new Company("Apple Inc.", "AAPL", "Images/Apple.png")),
                new SelectableData<Company>(new Company("Facebook, Inc.", "FB", "Images/Facebook.png")),
                new SelectableData<Company>(new Company("Alphabet Inc.", "GOOGL", "Images/Google.png")),
                new SelectableData<Company>(new Company("HP Inc", "HPQ", "Images/HP.png")),
                new SelectableData<Company>(new Company("International Business Machines Corporation", "IBM", "Images/IBM.png")),
                new SelectableData<Company>(new Company("Intel Corporation", "INTC", "Images/Intel.png")),
                new SelectableData<Company>(new Company("Microsoft Corporation", "MSFT", "Images/Microsoft.png")),
                new SelectableData<Company>(new Company("Oracle Corporation", "ORCL", "Images/Oracle.png")),
                new SelectableData<Company>(new Company("Twitter, Inc.", "TWTR", "Images/Twitter.png"))
            };
            companiesListView.ItemsSource = companiesDataList;
        }

        //Get companies list, currently selected with the switches
        private List<Company> GetSelectedCompaniesList()
        {
            List<Company> selectedCompanies = new List<Company>();
            for (int i = 0; i < companiesDataList.Count; i++)
                if (companiesDataList[i].isSelected) selectedCompanies.Add(companiesDataList[i].data);

            return selectedCompanies;
        }

        #endregion

    }
}
