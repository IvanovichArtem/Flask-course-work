from fpdf import FPDF


class Ticket(FPDF):
    def header(self):
        # Setting up the ticket header
        self.add_font("DejaVu", "", "tickets/DejaVuSansCondensed.ttf", uni=True)
        self.set_font("DejaVu", "", 24)
        self.cell(0, 10, "Минский Музей Исскуств", ln=True, align="C")
        self.ln(10)  # Add additional vertical spacing

    def footer(self):
        # Setting up the ticket footer
        self.add_font("DejaVu", "", "tickets/DejaVuSansCondensed.ttf", uni=True)
        self.set_font("DejaVu", "", 8)
        self.cell(0, 10, "Примечание:", 0, 1, "C")
        self.cell(
            0,
            10,
            "1: Вы можете придти в любой время работы музея и предъявить билеты брони и пойти на выставку",
            0,
            1,
            "C",
        )
        self.cell(
            0,
            10,
            "2: Запрещается фотографировать и записывать видео",
            0,
            1,
            "C",
        )
        self.cell(
            0,
            10,
            "3: При невозможности посещения мероприятия просим вас обратиться в службу поддержки нашего музея +375333333333",
            0,
            1,
            "C",
        )

    def ticket_content(self, ticket_data):
        # Generating the ticket content
        self.add_font("DejaVu", "", "tickets/DejaVuSansCondensed.ttf", uni=True)
        self.set_font("DejaVu", "", 17)
        indent = 20  # Specify the desired indentation value
        self.set_left_margin(
            indent
        )  # Set the left margin to create an indentation
        self.cell(0, 10, "ID брони: {}".format(ticket_data["id"]), 0, 1)
        self.cell(0, 10, "Название: {}".format(ticket_data["name"]), 0, 1)
        self.cell(0, 10, "Начало: {}".format(ticket_data["start_date"]), 0, 1)
        self.cell(0, 10, "Конец: {}".format(ticket_data["end_date"]), 0, 1)
        self.cell(0, 10, "Кол-во: {}".format(ticket_data["quantity"]), 0, 1)
        self.cell(
            0, 10, "Общая цена: {:.2f}".format(ticket_data["total_price"]), 0, 1
        )


def create_tickets(id, name, start_date, end_date, tickets_count, total_price):
    ticket_data = {
        "id": id,
        "name": name,
        "start_date": start_date,
        "end_date": end_date,
        "quantity": tickets_count,
        "total_price": total_price,
    }
    pdf = Ticket(format="a5", orientation="landscape")
    pdf.add_page()
    pdf.ticket_content(ticket_data)
    pdf.output(f"tickets/t/{id}.pdf")
