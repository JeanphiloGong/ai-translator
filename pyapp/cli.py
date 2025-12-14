import typer

from pyapp.services.translator import get_service

app = typer.Typer(help="AI Translator CLI")


def _print_result(result, show_grammar: bool) -> None:
    typer.echo(f"Original: {result.original_text}")
    typer.echo(f"English: {result.translated_text}")
    if show_grammar and result.english_grammar:
        typer.echo(f"English grammar: {result.english_grammar}")
    typer.echo(f"Japanese: {result.japanese_text}")
    typer.echo(f"Hiragana: {result.hiragana_pronunciation}")
    if show_grammar and result.japanese_grammar:
        typer.echo(f"Japanese grammar: {result.japanese_grammar}")
    typer.echo(f"Timestamp: {result.timestamp}")


@app.command("zh")
def translate_zh(
    text: str = typer.Argument(..., help="Chinese text to translate"),
    grammar: bool = typer.Option(False, "--grammar", help="Include grammar explanations"),
) -> None:
    svc = get_service()
    result = svc.translate_chinese(text, include_grammar=grammar)
    _print_result(result, grammar)


@app.command("en")
def correct_en(
    text: str = typer.Argument(..., help="English text to correct"),
    grammar: bool = typer.Option(False, "--grammar", help="Include grammar explanations"),
) -> None:
    svc = get_service()
    result = svc.correct_english(text, include_grammar=grammar)
    _print_result(result, grammar)


def main() -> None:
    app()


if __name__ == "__main__":
    main()

