from src.ai_engine.demo.loader import DemoCaseLoader

def main() -> None:
    loader = DemoCaseLoader()

    case = loader.load_case("bearing_healthy.json")
    print(case)
    print(case.case_id)
    print(case.scenario_type)
    print(case.timestamp)


if __name__ == "__main__":
    main()