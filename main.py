from gateway.worldometer_gateway import WorldOMeterGateway
from services.parser_service import ParserService
from services.wikipedia_service import WikipediaService

if __name__ == "__main__":
    worldometer_gateway = WorldOMeterGateway()
    parser_service = ParserService()

    latest_data = worldometer_gateway.fetch()
    output = parser_service.create_df_worldometer(latest_data)
    last_updated = parser_service.parse_last_updated(latest_data)
    output.to_csv(r'./cases.csv', index=False)
    output.set_index("Country/Other").to_json(r"./cases.json", orient="index")
    print(last_updated)
    print(output)

    today_output = parser_service.create_df_worldometer_by_day(latest_data, "main_table_countries_today")
    yesterday_output = parser_service.create_df_worldometer_by_day(latest_data, "main_table_countries_yesterday")
    today_output.to_csv(r'./cases_today.csv', index=False)
    today_output.set_index("Country/Other").to_json(r"./cases_today.json", orient="index")
    yesterday_output.to_csv(r'./cases_yesterday.csv', index=False)
    yesterday_output.set_index("Country/Other").to_json(r"./cases_yesterday.json", orient="index")

    wikipedia_service = WikipediaService()
    wikipedia_service.get_table()
