from html import escape


def render_email_html(subject: str, body: str) -> str:
    safe_subject = escape(subject)
    safe_body = escape(body).replace("\n", "<br>")

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>{safe_subject}</title>
    </head>
    <body style="margin:0;padding:0;background:#f4f4f4;
                 font-family:Arial,Helvetica,sans-serif;">

        <table role="presentation" width="100%" cellpadding="0"
               cellspacing="0" border="0"
               style="background:#f4f4f4;padding:24px 12px;">
            <tr>
                <td align="center">

                    <table role="presentation" width="100%" cellpadding="0"
                           cellspacing="0" border="0"
                           style="max-width:600px;background:#ffffff;
                                  border:1px solid #dcdcdc;">

                        <!-- Header -->
                        <tr>
                            <td style="padding:22px 28px;
                                       border-bottom:3px solid #164b83;">
                                <div style="font-size:20px;font-weight:bold;
                                            color:#164b83;">
                                    NTC
                                </div>
                                <div style="font-size:13px;color:#555555;
                                            margin-top:5px;">
                                    Ticket Management System
                                </div>
                            </td>
                        </tr>

                        <!-- Content -->
                        <tr>
                            <td style="padding:28px 28px 32px;">
                                <h1 style="margin:0 0 16px;
                                           font-size:20px;line-height:1.4;
                                           color:#1a1a1a;">
                                    {safe_subject}
                                </h1>

                                <div style="font-size:15px;line-height:1.6;
                                            color:#333333;
                                            word-break:break-word;">
                                    {safe_body}
                                </div>
                            </td>
                        </tr>

                        <!-- Footer -->
                        <tr>
                            <td style="padding:16px 28px;
                                       border-top:1px solid #e5e5e5;
                                       background:#fafafa;
                                       font-size:12px;line-height:1.5;
                                       color:#777777;">
                                This is an automated notification from the
                                NTC Ticket Management System.
                            </td>
                        </tr>

                    </table>

                </td>
            </tr>
        </table>
    </body>
    </html>
    """
