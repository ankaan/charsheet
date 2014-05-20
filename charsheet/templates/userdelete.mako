<%inherit file="base.mako"/>

<%block name="content">
    <div class="container">
        <div class="panel panel-default">
            <div class="panel-heading">
                <h1>Delete User</h1>
            </div>
            <div class="panel-body">
                <p>Are you sure you want to delete ${request.context.name}?</p>
                <p>Email: ${request.context.email}</p>
                ${form.render()|n}
            </div>
        </div>
    </div>
</%block>
